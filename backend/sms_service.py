"""
SMS Service: Sends research results via Twilio SMS
Handles validation, formatting, and rate limiting
"""

import os
import logging
import re
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class SMSValidationError(Exception):
    """Raised when SMS validation fails"""
    pass


class SMSRateLimitError(Exception):
    """Raised when SMS rate limit is exceeded"""
    pass


class SMSService:
    """Base SMS service"""

    async def send_sms(
        self,
        phone_number: str,
        research_data: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, str]:
        """Send research result via SMS"""
        raise NotImplementedError


class TwilioSMSService(SMSService):
    """Twilio SMS service for research result delivery"""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.twilio_client = None

        try:
            from twilio.rest import Client
            self.twilio_client = Client(account_sid, auth_token)
        except ImportError:
            logger.error("twilio package not installed")
            self.twilio_client = None

    def _validate_phone_number(self, phone_number: str) -> str:
        """
        Validate and normalize phone number to E.164 format.
        Only accepts US numbers for now.

        Args:
            phone_number: Phone number in various formats

        Returns:
            Normalized phone number in E.164 format (+1XXXXXXXXXX)

        Raises:
            SMSValidationError: If phone number is invalid
        """
        # Remove all non-digit characters
        digits = re.sub(r"\D", "", phone_number)

        # Handle 10-digit US number (add country code)
        if len(digits) == 10:
            digits = "1" + digits
        # Handle 11-digit number starting with 1 (US)
        elif len(digits) == 11 and digits.startswith("1"):
            pass
        # Handle already formatted E.164 (remove leading +)
        elif phone_number.startswith("+1") and len(digits) == 11:
            pass
        else:
            raise SMSValidationError(
                f"Invalid phone number: {phone_number}. "
                "Please provide a valid US phone number (10 digits)."
            )

        # Return in E.164 format
        return f"+{digits}"

    def _format_sms_message(self, research_data: Dict[str, Any]) -> str:
        """
        Format research data into concise SMS message (≤160 chars for single SMS).

        Args:
            research_data: Research result data

        Returns:
            Formatted SMS message
        """
        project_info = research_data.get("project_info", {})
        summary = research_data.get("summary", {})
        punch_list = research_data.get("punch_list", {})

        zip_code = project_info.get("zip", "")
        city = project_info.get("city", "")
        state = project_info.get("state", "")

        high_risk = summary.get("high_risk_count", 0)
        total_cost = summary.get("estimated_total_cost", 0)
        timeline = summary.get("estimated_timeline", "TBD")

        # Build concise message - aim for 160 chars for single SMS
        message = (
            f"RegGuard: {city}, {state} {zip_code}\n"
            f"⚠️  {high_risk} High Risks\n"
            f"💰 ${total_cost:,.0f}\n"
            f"⏱️  {timeline}\n"
            f"View full report: regguard.io"
        )

        # If message is too long, shorten further
        if len(message) > 160:
            message = (
                f"RegGuard {city}, {state}\n"
                f"Risks: {high_risk} | Cost: ${total_cost:,.0f}\n"
                f"Timeline: {timeline}\n"
                f"regguard.io"
            )

        return message

    async def send_sms(
        self,
        phone_number: str,
        research_data: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, str]:
        """
        Send research result via SMS using Twilio.

        Args:
            phone_number: Destination phone number
            research_data: Research result data to format
            user_id: User ID (for rate limiting checks - assumed done by caller)

        Returns:
            {
                "status": "sent",
                "message_id": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "phone": "+1XXXXXXXXXX"
            }

        Raises:
            SMSValidationError: If validation fails
            Exception: If Twilio API fails
        """
        if not self.twilio_client:
            raise Exception("Twilio client not initialized")

        # Validate and normalize phone number
        normalized_phone = self._validate_phone_number(phone_number)

        # Format message
        message_body = self._format_sms_message(research_data)

        logger.info(f"Sending SMS to {normalized_phone} for user {user_id}")

        try:
            # Send message via Twilio
            message = await asyncio.to_thread(
                self.twilio_client.messages.create,
                body=message_body,
                from_=self.from_number,
                to=normalized_phone,
            )

            logger.info(f"SMS sent successfully: {message.sid}")

            return {
                "status": "sent",
                "message_id": message.sid,
                "phone": normalized_phone,
            }

        except Exception as e:
            logger.error(f"Failed to send SMS to {normalized_phone}: {str(e)}")
            raise


class MockSMSService(SMSService):
    """Mock SMS service for testing and development"""

    def __init__(self):
        self.sent_messages = []

    def _validate_phone_number(self, phone_number: str) -> str:
        """Validate phone number format"""
        digits = re.sub(r"\D", "", phone_number)

        if len(digits) == 10:
            digits = "1" + digits
        elif len(digits) == 11 and digits.startswith("1"):
            pass
        else:
            raise SMSValidationError(
                f"Invalid phone number: {phone_number}. "
                "Please provide a valid US phone number."
            )

        return f"+{digits}"

    async def send_sms(
        self,
        phone_number: str,
        research_data: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, str]:
        """Mock SMS send - returns success without actually sending"""
        normalized_phone = self._validate_phone_number(phone_number)

        message_id = f"SM{uuid.uuid4().hex[:30].upper()}"
        self.sent_messages.append(
            {
                "phone": normalized_phone,
                "user_id": user_id,
                "message_id": message_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return {
            "status": "sent",
            "message_id": message_id,
            "phone": normalized_phone,
        }


def get_sms_service() -> SMSService:
    """Get SMS service instance based on environment configuration"""
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")

    if twilio_account_sid and twilio_auth_token and twilio_from_number:
        return TwilioSMSService(twilio_account_sid, twilio_auth_token, twilio_from_number)
    else:
        logger.warning("Twilio credentials not configured, using mock SMS service")
        return MockSMSService()
