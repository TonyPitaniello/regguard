"""
Email Service: Sends research memos to trial users
Supports SendGrid, Resend, or simple email backend
"""

import os
import logging
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
            logger.error("SendGrid not configured")
            return False

        try:
            message = self.Mail(
                from_email=os.getenv("RESEND_FROM_EMAIL", "noreply@regguardagent.com"),
                to_emails=to_email,
                subject="Your RegGuard Free Research Memo is Ready",
                html_content=self._build_html_email(address, research_memo, trial_id),
                plain_text_content=self._build_text_email(address, research_memo, trial_id),
            )

            response = self.sg.send(message)
            success = 200 <= response.status_code < 300

            if success:
                logger.info(f"Research memo sent to {to_email}")
            else:
                logger.error(f"SendGrid error: {response.status_code} {response.body}")

            return success

        except Exception as e:
            logger.error(f"Error sending email via SendGrid: {e}")
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
            logger.error("Resend not configured")
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

            # Resend API call
            try:
                response = self.resend.Emails.send({
                    "from": os.getenv("RESEND_FROM_EMAIL", "noreply@regguardagent.com"),
                    "to": to_email,
                    "subject": "Your Site Diligence Research Memo",
                    "html": html_content,
                })
            except Exception as e:
                logger.error(f"❌ Resend API error: {e}")
                return False

            success = response.get("id") is not None

            if success:
                logger.info(f"Research memo sent to {to_email} via Resend")
            else:
                logger.error(f"Resend error: {response}")

            return success

        except Exception as e:
            logger.error(f"Error sending email via Resend: {e}")
            return False


def get_email_service() -> Optional[EmailService]:
    """Get configured email service (SendGrid or Resend)"""
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    resend_key = os.getenv("RESEND_API_KEY")

    if sendgrid_key:
        logger.info("Using SendGrid email service")
        return SendGridEmailService(sendgrid_key)
    elif resend_key:
        logger.info("Using Resend email service")
        return ResendEmailService(resend_key)
    else:
        logger.warning("No email service configured (SENDGRID_API_KEY or RESEND_API_KEY not set)")
        return None
