"""
Email Service: Sends research memos to trial users
Supports SendGrid, Resend, or simple email backend
"""

import os
import logging
import traceback
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Base email service"""

    async def send_research_memo(
        self,
        to_email: str,
        address: str,
        research_memo: str,
        trial_id: str,
    ) -> bool:
        """Send research memo to trial user"""
        raise NotImplementedError

    async def send_research_result(
        self,
        to_email: str,
        research_data: dict,
    ) -> dict:
        """Send research result to user email. Returns dict with status and email_id."""
        raise NotImplementedError


class SendGridEmailService(EmailService):
    """SendGrid email service"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            self.sg = SendGridAPIClient(api_key)
            self.Mail = Mail
        except ImportError:
            logger.error("sendgrid package not installed")
            self.sg = None
            self.Mail = None

    async def send_research_memo(
        self,
        to_email: str,
        address: str,
        research_memo: str,
        trial_id: str,
    ) -> bool:
        """Send research memo via SendGrid"""
        if not self.sg or not self.Mail:
            logger.error("❌ SendGrid not configured")
            return False

        try:
            logger.info(f"📧 Building SendGrid message for {to_email}...")
            message = self.Mail(
                from_email=os.getenv("RESEND_FROM_EMAIL", "noreply@regguardagent.com"),
                to_emails=to_email,
                subject="Your RegGuard Free Research Memo is Ready",
                html_content=self._build_html_email(address, research_memo, trial_id),
                plain_text_content=self._build_text_email(address, research_memo, trial_id),
            )

            logger.info(f"📧 Sending via SendGrid...")
            response = self.sg.send(message)
            success = 200 <= response.status_code < 300

            if success:
                logger.info(f"✅ Research memo sent to {to_email} via SendGrid (status: {response.status_code})")
            else:
                logger.error(f"❌ SendGrid error: {response.status_code} - {response.body}")

            return success

        except Exception as e:
            logger.error(f"❌ Error sending email via SendGrid: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def _build_html_email(self, address: str, research_memo: str, trial_id: str) -> str:
        """Build HTML email with research memo"""
        memo_html = research_memo.replace("\n", "<br>")
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td style="padding: 30px 20px;">
                <table width="100%" style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr style="background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);">
                        <td style="padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 600;">Your Research Memo</h1>
                        </td>
                    </tr>
                    
                    <!-- Memo Content -->
                    <tr>
                        <td style="padding: 30px; font-size: 14px; line-height: 1.7; color: #2c3e50;">
                            <pre style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace; white-space: pre-wrap; word-wrap: break-word; margin: 0; color: #2c3e50; background: #f9fafb; padding: 20px; border-radius: 6px; border-left: 4px solid #4f46e5; font-size: 13px; line-height: 1.6;">{memo_html}</pre>
                        </td>
                    </tr>
                    
                    <!-- CTA -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px; text-align: center;">
                            <div style="background: linear-gradient(135deg, #f0f7ff 0%, #f3e8ff 100%); padding: 25px; border-radius: 6px; margin: 20px 0;">
                                <p style="margin: 0 0 15px 0; font-size: 14px; font-weight: 600; color: #1f2937;">
                                    Ready for the Complete Report?
                                </p>
                                <p style="margin: 0 0 20px 0; font-size: 13px; color: #555;">
                                    The premium report includes actionable punch list, complete permit package, and full environmental assessment.
                                </p>
                                <a href="https://app.regguardagent.com/order?trial={trial_id}" style="display: inline-block; background: #4f46e5; color: white; padding: 12px 28px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 13px;">
                                    Upgrade Now ($15,000)
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr style="border-top: 1px solid #e5e7eb;">
                        <td style="padding: 20px 30px; text-align: center; font-size: 12px; color: #888;">
                            <p style="margin: 0;">Questions? Reply to this email or contact <strong>support@regguardagent.com</strong></p>
                            <p style="margin: 5px 0 0 0;">RegGuard © 2026</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """

    def _build_text_email(self, address: str, research_memo: str, trial_id: str) -> str:
        """Build plain text email"""
        return f"""{research_memo}

───────────────────────────────────────────────────────────────
UPGRADE TO FULL REPORT ($15,000)
───────────────────────────────────────────────────────────────

This memo gives you research direction. The premium report includes:
✓ Actionable punch list (what to do)
✓ Complete permit package (ready to file)
✓ Full environmental assessment
✓ Professional formatting

Ready? Get your complete analysis:
https://app.regguardagent.com/order?trial={trial_id}

Questions? Reply to this email.

RegGuard © 2026
"""

    def _build_result_html_email(self, research_data: dict) -> str:
        """Build professional HTML email for research result delivery"""
        project_info = research_data.get("project_info", {})
        summary = research_data.get("summary", {})
        punch_list = research_data.get("punch_list", {})
        environmental = research_data.get("environmental_screening", {})

        address = project_info.get("address", "Unknown Address")
        city = project_info.get("city", "")
        state = project_info.get("state", "")
        zip_code = project_info.get("zip", "")

        high_risk = summary.get("high_risk_count", 0)
        total_risks = summary.get("total_environmental_risks", 0)
        total_cost = summary.get("estimated_total_cost", 0)
        timeline = summary.get("estimated_timeline", "")
        total_items = summary.get("total_punch_list_items", 0)
        honesty = research_data.get("honesty") or {}
        unverified = (
            research_data.get("preview")
            or summary.get("estimates_unverified")
            or not honesty.get("cost_verified")
        )
        risk_verified = honesty.get("risk_verified") is True
        cost_label = "Est. Total Cost (unverified)" if unverified else "Est. Total Cost"
        timeline_label = "Timeline (unverified)" if unverified else "Timeline"
        honesty_banner = ""
        if unverified or not risk_verified:
            honesty_banner = (
                '<tr><td style="padding: 16px 30px; background: #fff7ed; border-bottom: 1px solid #fed7aa;">'
                '<p style="margin: 0; font-size: 13px; color: #9a3412; line-height: 1.5;">'
                '<strong>Preview / unverified estimates.</strong> '
                'Environmental risk scores are not parcel-verified GIS data. '
                'Dollar and day figures are not AHJ quotes — confirm before bidding.'
                '</p></td></tr>'
            )
        risk_items_label = "High Risk Items" if risk_verified else "Risk score"
        risk_items_value = high_risk if risk_verified else "Unavailable"
        risk_items_color = "#dc2626" if risk_verified else "#9a3412"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td style="padding: 30px 20px;">
                <table width="100%" style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr style="background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);">
                        <td style="padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 700;">RegGuard Research Results</h1>
                            <p style="margin: 8px 0 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">Site Diligence Analysis Complete</p>
                        </td>
                    </tr>
                    
                    <!-- Project Info -->
                    <tr>
                        <td style="padding: 30px; border-bottom: 1px solid #e5e7eb;">
                            <h2 style="margin: 0 0 15px 0; font-size: 16px; color: #1f2937; font-weight: 600;">📍 Project Location</h2>
                            <p style="margin: 0; font-size: 14px; color: #4b5563; line-height: 1.6;">
                                <strong>{address}</strong><br>
                                {city}, {state} {zip_code}
                            </p>
                        </td>
                    </tr>
                    
                    {honesty_banner}
                    <!-- Risk Summary -->
                    <tr>
                        <td style="padding: 30px; border-bottom: 1px solid #e5e7eb;">
                            <h2 style="margin: 0 0 20px 0; font-size: 16px; color: #1f2937; font-weight: 600;">⚠️ Risk Assessment</h2>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0;">
                                        <span style="font-size: 13px; color: #6b7280;">Total Environmental Risks</span>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; color: #1f2937; font-weight: 600;">{total_risks}</p>
                                    </td>
                                    <td style="padding: 12px 0 12px 20px; border-bottom: 1px solid #f0f0f0; text-align: right;">
                                        <span style="font-size: 13px; color: {risk_items_color};">{risk_items_label}</span>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; color: {risk_items_color}; font-weight: 600;">{risk_items_value}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <span style="font-size: 13px; color: #6b7280;">{timeline_label}</span>
                                        <p style="margin: 5px 0 0 0; font-size: 16px; color: #1f2937; font-weight: 500;">{timeline}</p>
                                    </td>
                                    <td style="padding: 12px 0 0 20px; text-align: right;">
                                        <span style="font-size: 13px; color: #6b7280;">{cost_label}</span>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; color: #059669; font-weight: 600;">${total_cost:,.0f}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Action Items -->
                    <tr>
                        <td style="padding: 30px; border-bottom: 1px solid #e5e7eb;">
                            <h2 style="margin: 0 0 15px 0; font-size: 16px; color: #1f2937; font-weight: 600;">✓ Action Items</h2>
                            <p style="margin: 0 0 12px 0; font-size: 13px; color: #6b7280;">
                                <strong>{total_items}</strong> items on your punch list
                            </p>
                            <div style="background: #f9fafb; padding: 15px; border-radius: 6px; border-left: 3px solid #4f46e5;">
                                <p style="margin: 0; font-size: 13px; color: #4b5563; line-height: 1.6;">
                                    Your customized punch list includes all critical items, responsible parties, estimated timelines, and costs. Ready to tackle your project? Log in to view the complete breakdown.
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- CTA -->
                    <tr>
                        <td style="padding: 30px; text-align: center;">
                            <a href="https://app.regguardagent.com/results" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%); color: white; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 14px; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);">
                                View Full Research Report
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr style="background: #f9fafb; border-top: 1px solid #e5e7eb;">
                        <td style="padding: 25px 30px; text-align: center;">
                            <p style="margin: 0 0 10px 0; font-size: 12px; color: #888;">
                                Questions? Contact <strong>support@regguardagent.com</strong>
                            </p>
                            <p style="margin: 5px 0 0 0; font-size: 11px; color: #aaa;">
                                RegGuard © 2026 • Site Diligence Research Platform
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """

    async def send_research_result(
        self,
        to_email: str,
        research_data: dict,
    ) -> dict:
        """Send research result via SendGrid"""
        if not self.sg or not self.Mail:
            logger.error("❌ SendGrid not configured")
            raise Exception("SendGrid not configured")

        try:
            project_info = research_data.get("project_info", {})
            city = project_info.get("city", "Unknown")
            state = project_info.get("state", "")

            logger.info(f"📧 Building SendGrid result email for {to_email}...")
            message = self.Mail(
                from_email=os.getenv("RESEND_FROM_EMAIL", "noreply@regguardagent.com"),
                to_emails=to_email,
                subject=f"Your RegGuard Research Results - {city}, {state}",
                html_content=self._build_result_html_email(research_data),
            )

            logger.info(f"📧 Sending result via SendGrid...")
            response = self.sg.send(message)
            success = 200 <= response.status_code < 300

            if success:
                logger.info(f"✅ Research result sent to {to_email} via SendGrid")
                return {
                    "status": "sent",
                    "email_id": getattr(response, "headers", {}).get("X-Message-ID", ""),
                    "email": to_email,
                }
            else:
                logger.error(f"❌ SendGrid error: {response.status_code}")
                raise Exception(f"SendGrid error: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Error sending result via SendGrid: {str(e)}")
            raise


class ResendEmailService(EmailService):
    """Resend email service (alternative to SendGrid)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.resend = None
        
        try:
            import resend as resend_lib
            logger.info("📦 resend module imported successfully")
            
            # Configure Resend with API key
            resend_lib.api_key = api_key
            self.resend = resend_lib
            logger.info(f"✅ Resend initialized with API key: {api_key[:20]}...")
        except ImportError as e:
            logger.error(f"❌ resend package not installed. Install with: pip install resend")
            logger.error(f"   ImportError: {e}")
            self.resend = None
        except AttributeError as e:
            logger.error(f"❌ Error setting resend.api_key: {e}")
            self.resend = None
        except Exception as e:
            logger.error(f"❌ Unexpected error initializing Resend: {type(e).__name__}: {e}")
            self.resend = None

    async def send_research_memo(
        self,
        to_email: str,
        address: str,
        research_memo: str,
        trial_id: str,
    ) -> bool:
        """Send research memo via Resend"""
        if not self.resend:
            logger.error("❌ Resend not configured")
            return False

        try:
            # Simple, clean HTML email with preformatted memo
            memo_html = research_memo.replace("\n", "<br>")
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td style="padding: 30px 20px;">
                <table width="100%" style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr style="background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);">
                        <td style="padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 600;">Your Research Memo</h1>
                        </td>
                    </tr>
                    
                    <!-- Memo Content -->
                    <tr>
                        <td style="padding: 30px; font-size: 14px; line-height: 1.7; color: #2c3e50;">
                            <pre style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace; white-space: pre-wrap; word-wrap: break-word; margin: 0; color: #2c3e50; background: #f9fafb; padding: 20px; border-radius: 6px; border-left: 4px solid #4f46e5; font-size: 13px; line-height: 1.6;">{memo_html}</pre>
                        </td>
                    </tr>
                    
                    <!-- CTA -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px; text-align: center;">
                            <div style="background: linear-gradient(135deg, #f0f7ff 0%, #f3e8ff 100%); padding: 25px; border-radius: 6px; margin: 20px 0;">
                                <p style="margin: 0 0 15px 0; font-size: 14px; font-weight: 600; color: #1f2937;">
                                    Ready for the Complete Report?
                                </p>
                                <p style="margin: 0 0 20px 0; font-size: 13px; color: #555;">
                                    The premium report includes actionable punch list, complete permit package, and full environmental assessment.
                                </p>
                                <a href="https://app.regguardagent.com/order?trial={trial_id}" style="display: inline-block; background: #4f46e5; color: white; padding: 12px 28px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 13px;">
                                    Upgrade Now ($15,000)
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr style="border-top: 1px solid #e5e7eb;">
                        <td style="padding: 20px 30px; text-align: center; font-size: 12px; color: #888;">
                            <p style="margin: 0;">Questions? Reply to this email or contact <strong>support@regguardagent.com</strong></p>
                            <p style="margin: 5px 0 0 0;">RegGuard © 2026</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
            """

            logger.info(f"📧 Preparing Resend API call for {to_email}...")
            # Resend API call
            try:
                logger.info(f"📧 Calling Resend.Emails.send()...")
                response = self.resend.Emails.send({
                    "from": os.getenv("RESEND_FROM_EMAIL", "noreply@regguardagent.com"),
                    "to": to_email,
                    "subject": "Your Site Diligence Research Memo",
                    "html": html_content,
                })
                logger.info(f"📧 Resend response: {response}")
            except Exception as e:
                logger.error(f"❌ Resend API error: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False

            success = response.get("id") is not None

            if success:
                logger.info(f"✅ Research memo sent to {to_email} via Resend (id: {response.get('id')})")
            else:
                logger.error(f"❌ Resend error: {response}")

            return success

        except Exception as e:
            logger.error(f"❌ Error sending email via Resend: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    async def send_research_result(
        self,
        to_email: str,
        research_data: dict,
    ) -> dict:
        """Send research result via Resend"""
        if not self.resend:
            logger.error("❌ Resend not configured")
            raise Exception("Resend not configured")

        try:
            project_info = research_data.get("project_info", {})
            city = project_info.get("city", "Unknown")
            state = project_info.get("state", "")

            html_content = self._build_result_html_email(research_data)

            logger.info(f"📧 Preparing Resend API call for result to {to_email}...")
            response = self.resend.Emails.send({
                "from": os.getenv("RESEND_FROM_EMAIL", "noreply@regguardagent.com"),
                "to": to_email,
                "subject": f"Your RegGuard Research Results - {city}, {state}",
                "html": html_content,
            })
            logger.info(f"📧 Resend response: {response}")

            if response.get("id"):
                logger.info(f"✅ Research result sent to {to_email} via Resend")
                return {
                    "status": "sent",
                    "email_id": response.get("id", ""),
                    "email": to_email,
                }
            else:
                logger.error(f"❌ Resend error: {response}")
                raise Exception(f"Resend error: {response}")

        except Exception as e:
            logger.error(f"❌ Error sending result via Resend: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _build_result_html_email(self, research_data: dict) -> str:
        """Build professional HTML email for research result delivery"""
        project_info = research_data.get("project_info", {})
        summary = research_data.get("summary", {})
        punch_list = research_data.get("punch_list", {})

        address = project_info.get("address", "Unknown Address")
        city = project_info.get("city", "")
        state = project_info.get("state", "")
        zip_code = project_info.get("zip", "")

        high_risk = summary.get("high_risk_count", 0)
        total_risks = summary.get("total_environmental_risks", 0)
        total_cost = summary.get("estimated_total_cost", 0)
        timeline = summary.get("estimated_timeline", "")
        total_items = summary.get("total_punch_list_items", 0)
        honesty = research_data.get("honesty") or {}
        unverified = (
            research_data.get("preview")
            or summary.get("estimates_unverified")
            or not honesty.get("cost_verified")
        )
        risk_verified = honesty.get("risk_verified") is True
        cost_label = "Est. Total Cost (unverified)" if unverified else "Est. Total Cost"
        timeline_label = "Timeline (unverified)" if unverified else "Timeline"
        honesty_banner = ""
        if unverified or not risk_verified:
            honesty_banner = (
                '<tr><td style="padding: 16px 30px; background: #fff7ed; border-bottom: 1px solid #fed7aa;">'
                '<p style="margin: 0; font-size: 13px; color: #9a3412; line-height: 1.5;">'
                '<strong>Preview / unverified estimates.</strong> '
                'Environmental risk scores are not parcel-verified GIS data. '
                'Dollar and day figures are not AHJ quotes — confirm before bidding.'
                '</p></td></tr>'
            )
        risk_items_label = "High Risk Items" if risk_verified else "Risk score"
        risk_items_value = high_risk if risk_verified else "Unavailable"
        risk_items_color = "#dc2626" if risk_verified else "#9a3412"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td style="padding: 30px 20px;">
                <table width="100%" style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr style="background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);">
                        <td style="padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 700;">RegGuard Research Results</h1>
                            <p style="margin: 8px 0 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">Site Diligence Analysis Complete</p>
                        </td>
                    </tr>
                    
                    <!-- Project Info -->
                    <tr>
                        <td style="padding: 30px; border-bottom: 1px solid #e5e7eb;">
                            <h2 style="margin: 0 0 15px 0; font-size: 16px; color: #1f2937; font-weight: 600;">📍 Project Location</h2>
                            <p style="margin: 0; font-size: 14px; color: #4b5563; line-height: 1.6;">
                                <strong>{address}</strong><br>
                                {city}, {state} {zip_code}
                            </p>
                        </td>
                    </tr>
                    
                    {honesty_banner}
                    <!-- Risk Summary -->
                    <tr>
                        <td style="padding: 30px; border-bottom: 1px solid #e5e7eb;">
                            <h2 style="margin: 0 0 20px 0; font-size: 16px; color: #1f2937; font-weight: 600;">⚠️ Risk Assessment</h2>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0;">
                                        <span style="font-size: 13px; color: #6b7280;">Total Environmental Risks</span>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; color: #1f2937; font-weight: 600;">{total_risks}</p>
                                    </td>
                                    <td style="padding: 12px 0 12px 20px; border-bottom: 1px solid #f0f0f0; text-align: right;">
                                        <span style="font-size: 13px; color: {risk_items_color};">{risk_items_label}</span>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; color: {risk_items_color}; font-weight: 600;">{risk_items_value}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <span style="font-size: 13px; color: #6b7280;">{timeline_label}</span>
                                        <p style="margin: 5px 0 0 0; font-size: 16px; color: #1f2937; font-weight: 500;">{timeline}</p>
                                    </td>
                                    <td style="padding: 12px 0 0 20px; text-align: right;">
                                        <span style="font-size: 13px; color: #6b7280;">{cost_label}</span>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; color: #059669; font-weight: 600;">${total_cost:,.0f}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Action Items -->
                    <tr>
                        <td style="padding: 30px; border-bottom: 1px solid #e5e7eb;">
                            <h2 style="margin: 0 0 15px 0; font-size: 16px; color: #1f2937; font-weight: 600;">✓ Action Items</h2>
                            <p style="margin: 0 0 12px 0; font-size: 13px; color: #6b7280;">
                                <strong>{total_items}</strong> items on your punch list
                            </p>
                            <div style="background: #f9fafb; padding: 15px; border-radius: 6px; border-left: 3px solid #4f46e5;">
                                <p style="margin: 0; font-size: 13px; color: #4b5563; line-height: 1.6;">
                                    Your customized punch list includes all critical items, responsible parties, estimated timelines, and costs. Ready to tackle your project? Log in to view the complete breakdown.
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- CTA -->
                    <tr>
                        <td style="padding: 30px; text-align: center;">
                            <a href="https://app.regguardagent.com/results" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%); color: white; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 14px; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);">
                                View Full Research Report
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr style="background: #f9fafb; border-top: 1px solid #e5e7eb;">
                        <td style="padding: 25px 30px; text-align: center;">
                            <p style="margin: 0 0 10px 0; font-size: 12px; color: #888;">
                                Questions? Contact <strong>support@regguardagent.com</strong>
                            </p>
                            <p style="margin: 5px 0 0 0; font-size: 11px; color: #aaa;">
                                RegGuard © 2026 • Site Diligence Research Platform
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """


def get_email_service() -> Optional[EmailService]:
    """Get configured email service (SendGrid or Resend)"""
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    resend_key = os.getenv("RESEND_API_KEY")

    logger.info(f"🔍 Email service check: SendGrid={'SET' if sendgrid_key else 'NOT SET'}, Resend={'SET' if resend_key else 'NOT SET'}")

    if sendgrid_key:
        logger.info("📧 Using SendGrid email service")
        return SendGridEmailService(sendgrid_key)
    elif resend_key:
        logger.info("📧 Using Resend email service")
        return ResendEmailService(resend_key)
    else:
        logger.error("❌ No email service configured (SENDGRID_API_KEY or RESEND_API_KEY not set)")
        return None
