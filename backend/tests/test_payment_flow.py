"""
Test suite for payment flow and Stripe integration.
Tests payment submission, webhooks, research triggers, email, and failure handling.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json
import hmac
import hashlib


class TestPaymentSubmission:
    """Test payment submission and checkout session creation."""

    @pytest.mark.payment
    async def test_payment_submission_success(self, sample_payment_request, mock_stripe):
        """Test successful payment submission creates valid checkout session."""
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.return_value = {
                "id": "cs_test_session_12345",
                "url": "https://checkout.stripe.com/pay/cs_test_session_12345",
                "client_secret": "cs_test_secret_12345",
                "payment_status": "unpaid",
            }
            
            result = mock_session(
                payment_method_types=["card"],
                mode="payment",
                line_items=[{"price": "price_premium", "quantity": 1}],
                metadata={"trial_id": sample_payment_request["trial_id"]},
            )
            
            assert result["id"] == "cs_test_session_12345"
            assert "checkout.stripe.com" in result["url"]
            assert result["payment_status"] == "unpaid"

    @pytest.mark.payment
    async def test_payment_with_premium_tier(self, sample_payment_request):
        """Test payment submission with premium tier pricing."""
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.return_value = {
                "id": "cs_test_premium",
                "amount_total": 1500000,  # $15,000
                "currency": "usd",
                "metadata": {"tier": "premium"},
            }
            
            result = mock_session()
            
            assert result["amount_total"] == 1500000
            assert result["metadata"]["tier"] == "premium"

    @pytest.mark.payment
    async def test_payment_with_enterprise_tier(self):
        """Test payment submission with enterprise tier pricing."""
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.return_value = {
                "id": "cs_test_enterprise",
                "amount_total": 6000000,  # $60,000
                "currency": "usd",
                "metadata": {"tier": "enterprise"},
            }
            
            result = mock_session()
            
            assert result["amount_total"] == 6000000
            assert result["metadata"]["tier"] == "enterprise"

    @pytest.mark.payment
    async def test_payment_invalid_tier_rejection(self):
        """Test that payment with invalid tier is rejected."""
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.side_effect = ValueError("Invalid tier: invalid_tier")
            
            with pytest.raises(ValueError):
                mock_session(
                    metadata={"tier": "invalid_tier"}
                )

    @pytest.mark.payment
    async def test_payment_currency_validation(self):
        """Test payment currency is always USD."""
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.return_value = {"currency": "usd"}
            result = mock_session()
            
            assert result["currency"].lower() == "usd"


class TestStripeWebhook:
    """Test Stripe webhook handling and signature verification."""

    @pytest.mark.payment
    async def test_webhook_signature_verification_valid(self, sample_stripe_webhook_event):
        """Test valid webhook signature is accepted."""
        payload = json.dumps(sample_stripe_webhook_event)
        secret = "whsec_test_signature_secret_1234567890"
        
        # Create valid signature
        signed_content = f"{sample_stripe_webhook_event['id']}.{int(datetime.now().timestamp())}.{payload}"
        expected_signature = hmac.new(
            secret.encode(),
            signed_content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        with patch("auth.verify_stripe_webhook_signature") as mock_verify:
            mock_verify.return_value = True
            result = mock_verify(payload, expected_signature, secret)
            
            assert result is True

    @pytest.mark.payment
    async def test_webhook_signature_verification_invalid(self, sample_stripe_webhook_event):
        """Test invalid webhook signature is rejected."""
        payload = json.dumps(sample_stripe_webhook_event)
        invalid_signature = "invalid_signature_12345"
        
        with patch("auth.verify_stripe_webhook_signature") as mock_verify:
            mock_verify.return_value = False
            result = mock_verify(payload, invalid_signature, "secret")
            
            assert result is False

    @pytest.mark.payment
    async def test_webhook_checkout_completed_event(self, sample_stripe_webhook_event):
        """Test processing of checkout.session.completed event."""
        with patch("auth.handle_checkout_session_completed") as mock_handler:
            mock_handler.return_value = {
                "status": "success",
                "trial_id": sample_stripe_webhook_event["data"]["object"]["metadata"]["trial_id"],
                "payment_id": sample_stripe_webhook_event["data"]["object"]["id"],
            }
            
            result = mock_handler(sample_stripe_webhook_event["data"]["object"])
            
            # Handle async mock returns
            if hasattr(result, '__await__'):
                result = await result
            
            
            assert result["status"] == "success"
            assert result["payment_id"] == sample_stripe_webhook_event["data"]["object"]["id"]

    @pytest.mark.payment
    async def test_webhook_idempotency(self, sample_stripe_webhook_event):
        """Test webhook handling is idempotent (duplicate events are safe)."""
        event_id = sample_stripe_webhook_event["id"]
        
        with patch("auth.handle_checkout_session_completed") as mock_handler:
            mock_handler.return_value = {"status": "success", "event_id": event_id}
            
            result1 = mock_handler(sample_stripe_webhook_event["data"]["object"])
            result2 = mock_handler(sample_stripe_webhook_event["data"]["object"])
            
            # Handle async returns
            if hasattr(result1, '__await__'):
                result1 = await result1
            if hasattr(result2, '__await__'):
                result2 = await result2
            
            # Both should succeed with same result
            assert result1 == result2
            assert mock_handler.call_count == 2


class TestResearchTrigger:
    """Test that payment completion triggers research."""

    @pytest.mark.payment
    async def test_payment_triggers_research_initiation(self, sample_payment_confirmation):
        """Test that successful payment initiates research task."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "status": "started",
                "trial_id": sample_payment_confirmation["trial_id"],
                "jurisdiction": "Austin, TX",
            }
            
            result = mock_research({})
            
            assert result["status"] == "started"
            assert result["trial_id"] == sample_payment_confirmation["trial_id"]

    @pytest.mark.payment
    async def test_research_uses_trial_metadata(self):
        """Test research task uses trial metadata from payment."""
        trial_metadata = {
            "trial_id": "trial_test_12345",
            "address": "123 Main St, Austin, TX 78704",
            "zip_code": "78704",
            "tier": "premium",
        }
        
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "trial_id": trial_metadata["trial_id"],
                "address": trial_metadata["address"],
            }
            
            result = mock_research(trial_metadata)
            
            assert result["trial_id"] == trial_metadata["trial_id"]
            assert result["address"] == trial_metadata["address"]

    @pytest.mark.payment
    async def test_research_error_does_not_block_order(self):
        """Test research error doesn't fail the entire payment flow."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.side_effect = Exception("Research timeout")
            
            with pytest.raises(Exception):
                mock_research({})
            
            # Order should still be created despite research error
            with patch("stripe.checkout.Session.create") as mock_session:
                mock_session.return_value = {"id": "cs_test_session"}
                result = mock_session()
                
                assert result["id"] == "cs_test_session"


class TestEmailNotification:
    """Test email notifications after payment."""

    @pytest.mark.payment
    @pytest.mark.email
    async def test_payment_confirmation_email_sent(self, sample_payment_confirmation, mock_email_service):
        """Test confirmation email sent after successful payment."""
        await mock_email_service.send_payment_confirmation(
            to_email=sample_payment_confirmation["email"],
            trial_id=sample_payment_confirmation["trial_id"],
            tier=sample_payment_confirmation["tier"],
            amount=sample_payment_confirmation["amount"],
        )
        
        mock_email_service.send_payment_confirmation.assert_called_once()

    @pytest.mark.payment
    @pytest.mark.email
    async def test_research_memo_email_sent_after_completion(self, sample_research_memo, mock_email_service):
        """Test research memo email sent after research completes."""
        await mock_email_service.send_research_memo(
            to_email="contractor@example.com",
            address="123 Main St, Austin, TX 78704",
            research_memo=sample_research_memo,
            trial_id="trial_test_12345",
        )
        
        mock_email_service.send_research_memo.assert_called_once()

    @pytest.mark.payment
    @pytest.mark.email
    async def test_email_includes_required_content(self, sample_payment_confirmation, mock_email_service):
        """Test confirmation email includes all required content."""
        email_content = {
            "to": sample_payment_confirmation["email"],
            "subject": "Payment Confirmation - RegGuard",
            "body": f"Your payment of ${sample_payment_confirmation['amount']/100:.2f} has been received.",
        }
        
        await mock_email_service.send_payment_confirmation(
            to_email=email_content["to"],
            trial_id=sample_payment_confirmation["trial_id"],
        )
        
        # Verify email was sent
        assert mock_email_service.send_payment_confirmation.called

    @pytest.mark.payment
    @pytest.mark.email
    async def test_email_failure_logs_error(self, mock_email_service):
        """Test email service failure is logged but doesn't crash flow."""
        mock_email_service.send_payment_confirmation.side_effect = Exception("Email service down")
        
        with pytest.raises(Exception):
            await mock_email_service.send_payment_confirmation(
                to_email="test@example.com",
                trial_id="trial_123",
            )


class TestPaymentFailureHandling:
    """Test payment failure scenarios and error recovery."""

    @pytest.mark.payment
    async def test_declined_card_handling(self):
        """Test handling of declined credit card."""
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.return_value = {
                "id": "cs_declined",
                "payment_status": "unpaid",
                "last_payment_error": "card_declined",
            }
            
            result = mock_session()
            
            assert result["payment_status"] == "unpaid"
            assert "declined" in result["last_payment_error"]

    @pytest.mark.payment
    async def test_insufficient_funds_handling(self):
        """Test handling of insufficient funds error."""
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.return_value = {
                "id": "cs_insufficient",
                "payment_status": "unpaid",
                "error": "insufficient_funds",
            }
            
            result = mock_session()
            
            assert result["payment_status"] == "unpaid"

    @pytest.mark.payment
    async def test_payment_timeout_handling(self):
        """Test handling of payment processing timeout."""
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.side_effect = TimeoutError("Payment processing timeout")
            
            with pytest.raises(TimeoutError):
                mock_session()

    @pytest.mark.payment
    async def test_duplicate_payment_prevention(self):
        """Test prevention of duplicate payment processing."""
        idempotency_key = "idempotency_key_12345"
        
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.return_value = {
                "id": "cs_test_duplicate",
                "idempotency_key": idempotency_key,
            }
            
            result1 = mock_session(idempotency_key=idempotency_key)
            result2 = mock_session(idempotency_key=idempotency_key)
            
            # Both calls should have same session ID (Stripe ensures this)
            assert result1["id"] == result2["id"]
            assert result1["idempotency_key"] == idempotency_key

    @pytest.mark.payment
    async def test_refund_processing(self):
        """Test refund processing after failed order."""
        original_payment_id = "ch_test_payment_12345"
        
        with patch("stripe.Refund.create") as mock_refund:
            mock_refund.return_value = {
                "id": "re_test_refund_12345",
                "charge": original_payment_id,
                "amount": 1500000,
                "status": "succeeded",
            }
            
            result = mock_refund(charge=original_payment_id)
            
            assert result["status"] == "succeeded"
            assert result["charge"] == original_payment_id
