"""
Unified Stripe Integration Service
Handles checkout sessions, webhooks, and order management for all customer segments.
Supports tiers: 'free', 'contractor_pro', 'ic_consultant', 'sponsor'
"""

import os
import logging
import stripe
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Tier pricing configuration
TIER_PRICING = {
    "free": {
        "name": "Free Tier",
        "price_id": None,
        "amount_cents": 0,
    },
    "contractor_pro": {
        "name": "Contractor Pro",
        "price_id": os.getenv("STRIPE_PRICE_CONTRACTOR_PRO"),
        "amount_cents": 9900,  # $99/month
    },
    "ic_consultant": {
        "name": "IC Consultant",
        "price_id": os.getenv("STRIPE_PRICE_IC_CONSULTANT"),
        "amount_cents": 19900,  # $199/month
    },
    "sponsor": {
        "name": "Sponsor Admin",
        "price_id": os.getenv("STRIPE_PRICE_SPONSOR"),
        "amount_cents": 49900,  # $499/month
    },
}


class CheckoutRequest(BaseModel):
    """Request to create checkout session"""
    user_id: str
    tier: str
    success_url: str
    cancel_url: str


class OrderResponse(BaseModel):
    """Order representation"""
    id: str
    user_id: str
    stripe_session_id: Optional[str]
    stripe_payment_intent_id: Optional[str]
    amount: int
    currency: str
    status: str  # pending, completed, failed
    tier: str
    created_at: str
    updated_at: str


def is_stripe_configured() -> bool:
    """Check if Stripe is properly configured"""
    return bool(stripe.api_key and STRIPE_WEBHOOK_SECRET)


async def create_checkout_session(
    user_id: str,
    tier: str,
    success_url: str = "https://localhost:5173/checkout/success",
    cancel_url: str = "https://localhost:5173/checkout/cancel",
) -> Dict[str, Any]:
    """
    Create a Stripe Checkout Session for the specified tier.
    
    Args:
        user_id: UUID of the user
        tier: One of 'free', 'contractor_pro', 'ic_consultant', 'sponsor'
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
    
    Returns:
        {
            "checkout_url": "https://checkout.stripe.com/...",
            "session_id": "cs_...",
        }
    
    Raises:
        ValueError: If tier is invalid or Stripe is not configured
    """
    if not is_stripe_configured():
        raise ValueError("Stripe is not configured. Set STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET.")
    
    if tier not in TIER_PRICING:
        raise ValueError(f"Invalid tier: {tier}")
    
    if tier == "free":
        return {
            "checkout_url": None,
            "session_id": None,
            "message": "Free tier - no payment required"
        }
    
    try:
        tier_config = TIER_PRICING[tier]
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": tier_config["price_id"],
                    "quantity": 1,
                }
            ],
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            metadata={
                "user_id": user_id,
                "tier": tier,
            },
        )
        
        logger.info(f"✅ Checkout session created: {session.id} for user {user_id}")
        
        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"❌ Stripe error creating checkout: {e}")
        raise ValueError(f"Failed to create checkout session: {str(e)}") from e
    except Exception as e:
        logger.error(f"❌ Unexpected error creating checkout: {e}")
        raise ValueError(f"Unexpected error: {str(e)}") from e


async def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve an order from the database.
    
    In production: query Supabase
    For now: placeholder implementation
    """
    logger.info(f"📋 Retrieving order: {order_id}")
    # TODO: Implement Supabase query
    return None


async def get_user_orders(user_id: str, limit: int = 10) -> list:
    """
    Retrieve all orders for a user.
    
    In production: query Supabase
    For now: placeholder implementation
    """
    logger.info(f"📋 Retrieving orders for user: {user_id}")
    # TODO: Implement Supabase query
    return []


async def handle_webhook(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Stripe webhook events.
    
    Supported events:
    - checkout.session.completed
    - invoice.payment_succeeded
    - invoice.payment_failed
    - customer.subscription.deleted
    """
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})
    
    logger.info(f"🔔 Processing webhook: {event_type}")
    
    try:
        if event_type == "checkout.session.completed":
            return await handle_checkout_session_completed(data)
        
        elif event_type == "invoice.payment_succeeded":
            return await handle_invoice_payment_succeeded(data)
        
        elif event_type == "invoice.payment_failed":
            return await handle_invoice_payment_failed(data)
        
        elif event_type == "customer.subscription.deleted":
            return await handle_subscription_deleted(data)
        
        else:
            logger.info(f"ℹ️ Unhandled event type: {event_type}")
            return {"status": "unhandled"}
    
    except Exception as e:
        logger.error(f"❌ Error handling webhook: {e}")
        raise


async def handle_checkout_session_completed(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle checkout.session.completed event.
    Updates order status to 'completed' and triggers post-payment actions.
    """
    session_id = session_data.get("id")
    metadata = session_data.get("metadata", {})
    user_id = metadata.get("user_id")
    tier = metadata.get("tier")
    
    logger.info(f"✅ Checkout session completed: {session_id} for user {user_id}")
    
    # TODO: Update order status in Supabase to 'completed'
    # TODO: Update user tier in profiles table
    # TODO: Send confirmation email
    
    return {
        "status": "success",
        "session_id": session_id,
        "user_id": user_id,
        "tier": tier,
    }


async def handle_invoice_payment_succeeded(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle invoice.payment_succeeded event.
    Recurring payment succeeded.
    """
    invoice_id = invoice_data.get("id")
    logger.info(f"💰 Invoice payment succeeded: {invoice_id}")
    
    # TODO: Update subscription status
    return {"status": "success", "invoice_id": invoice_id}


async def handle_invoice_payment_failed(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle invoice.payment_failed event.
    Recurring payment failed.
    """
    invoice_id = invoice_data.get("id")
    logger.warning(f"⚠️ Invoice payment failed: {invoice_id}")
    
    # TODO: Notify user
    # TODO: Update subscription status
    return {"status": "failed", "invoice_id": invoice_id}


async def handle_subscription_deleted(subscription_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle customer.subscription.deleted event.
    User cancelled their subscription.
    """
    subscription_id = subscription_data.get("id")
    logger.info(f"🔄 Subscription deleted: {subscription_id}")
    
    # TODO: Update user tier back to 'free'
    return {"status": "deleted", "subscription_id": subscription_id}


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify Stripe webhook signature.
    
    Args:
        payload: Raw request body
        signature: Stripe-Signature header
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not STRIPE_WEBHOOK_SECRET:
        logger.warning("⚠️ STRIPE_WEBHOOK_SECRET not set, skipping verification")
        return True
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )
        return True
    except ValueError:
        logger.warning("⚠️ Invalid webhook signature format")
        return False
    except stripe.error.SignatureVerificationError:
        logger.warning("⚠️ Webhook signature verification failed")
        return False
    except Exception as e:
        logger.error(f"❌ Error verifying webhook signature: {e}")
        return False
