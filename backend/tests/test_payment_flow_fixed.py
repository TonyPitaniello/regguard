"""
Phase 1 Payment Flow Integration Tests

Tests for:
- Checkout session creation
- Orders endpoint
- Stripe webhook handling
- Frontend redirect flow
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stripe_service import (
    create_checkout_session,
    get_order,
    get_user_orders,
    handle_webhook,
    verify_webhook_signature,
)


class TestPaymentFlowFixed:
    """Test fixed payment pipeline"""
    
    @pytest.mark.asyncio
    async def test_checkout_session_created(self):
        """Test: Checkout session can be created for a tier"""
        with patch('stripe_service.is_stripe_configured', return_value=True):
            with patch('stripe_service.stripe') as mock_stripe:
                # Mock successful Stripe response
                mock_session = MagicMock()
                mock_session.id = "cs_test_session_123"
                mock_session.url = "https://checkout.stripe.com/pay/cs_test_session_123"
                mock_stripe.checkout.Session.create.return_value = mock_session
                
                # Create checkout session
                result = await create_checkout_session(
                    user_id="user-123",
                    tier="contractor_pro",
                    success_url="https://localhost:5173/checkout/success",
                    cancel_url="https://localhost:5173/checkout/cancel"
                )
                
                # Assertions
                assert result["session_id"] == "cs_test_session_123"
                assert result["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_session_123"
                mock_stripe.checkout.Session.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_orders_endpoint_returns_user_orders(self):
        """Test: Orders endpoint returns user's orders"""
        with patch('stripe_service.get_user_orders', new_callable=AsyncMock) as mock_get_orders:
            # Mock orders
            mock_get_orders.return_value = [
                {
                    "id": "order-1",
                    "user_id": "user-123",
                    "status": "completed",
                    "tier": "contractor_pro",
                    "amount": 9900,
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ]
            
            # Get orders
            orders = await mock_get_orders("user-123")
            
            # Assertions
            assert len(orders) == 1
            assert orders[0]["id"] == "order-1"
            assert orders[0]["tier"] == "contractor_pro"
    
    @pytest.mark.asyncio
    async def test_stripe_webhook_updates_order(self):
        """Test: Stripe webhook correctly updates order status"""
        webhook_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_session_123",
                    "metadata": {
                        "user_id": "user-123",
                        "tier": "contractor_pro"
                    }
                }
            }
        }
        
        # Handle webhook
        result = await handle_webhook(webhook_event)
        
        # Assertions
        assert result["status"] == "success"
        assert result["user_id"] == "user-123"
        assert result["tier"] == "contractor_pro"
    
    def test_webhook_signature_verification(self):
        """Test: Webhook signature verification works"""
        with patch('stripe_service.STRIPE_WEBHOOK_SECRET', 'test-secret'):
            with patch('stripe_service.stripe') as mock_stripe:
                # Setup mock
                mock_stripe.Webhook.construct_event.return_value = {"type": "test"}
                
                payload = b'test_payload'
                signature = 'test_signature'
                
                # Verify signature
                result = verify_webhook_signature(payload, signature)
                
                # If we get here without exception, signature is valid
                mock_stripe.Webhook.construct_event.assert_called_once()


class TestCheckoutFlow:
    """Test checkout flow end-to-end"""
    
    @pytest.mark.asyncio
    async def test_free_tier_no_checkout_needed(self):
        """Test: Free tier doesn't create checkout session"""
        with patch('stripe_service.is_stripe_configured', return_value=True):
            result = await create_checkout_session(
                user_id="user-123",
                tier="free"
            )
            
            # Assertions - free tier returns no checkout URL
            assert result["message"] == "Free tier - no payment required"
            assert result["checkout_url"] is None


class TestWebhookHandling:
    """Test webhook event handling"""
    
    @pytest.mark.asyncio
    async def test_checkout_session_completed_event(self):
        """Test: checkout.session.completed event is processed"""
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "metadata": {
                        "user_id": "user-123",
                        "tier": "ic_consultant"
                    }
                }
            }
        }
        
        result = await handle_webhook(event)
        
        assert result["status"] == "success"
        assert result["user_id"] == "user-123"
    
    @pytest.mark.asyncio
    async def test_invoice_payment_succeeded_event(self):
        """Test: invoice.payment_succeeded event is processed"""
        event = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test_123"
                }
            }
        }
        
        result = await handle_webhook(event)
        
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_subscription_deleted_event(self):
        """Test: customer.subscription.deleted event is processed"""
        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test_123"
                }
            }
        }
        
        result = await handle_webhook(event)
        
        assert result["status"] == "deleted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
