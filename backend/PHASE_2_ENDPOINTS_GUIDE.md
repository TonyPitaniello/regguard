"""
Phase 2 Enterprise API Endpoints
To be added to main.py in FastAPI

These endpoints handle:
1. PDF generation and delivery
2. Stripe checkout and webhooks
3. Premium tier management
4. Order management
"""

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CheckoutRequest(BaseModel):
    """Request to start checkout"""
    trial_id: str
    tier: str  # "premium" or "enterprise"


class CheckoutResponse(BaseModel):
    """Response with checkout URL"""
    session_id: str
    checkout_url: str


class OrderResponse(BaseModel):
    """Order response"""
    order_id: str
    trial_id: str
    tier: str
    status: str
    created_at: str
    pdf_urls: Optional[Dict[str, str]] = None


class PDFGenerationRequest(BaseModel):
    """Request to generate PDFs"""
    trial_id: str
    tier: str


# ============================================================================
# ENDPOINTS (Add to main.py)
# ============================================================================

"""
# In main.py, add these endpoints:

@app.post("/checkout")
async def create_checkout(request: CheckoutRequest) -> CheckoutResponse:
    '''
    Create Stripe checkout session
    
    Args:
        request: CheckoutRequest with trial_id and tier
    
    Returns:
        Checkout session ID and URL
    
    Example:
        POST /checkout
        {
            "trial_id": "uuid-123",
            "tier": "premium"
        }
        
        Response:
        {
            "session_id": "cs_live_...",
            "checkout_url": "https://checkout.stripe.com/pay/cs_live_..."
        }
    '''
    from stripe_integration import create_checkout_session
    
    try:
        logger.info(f"💳 Creating checkout for trial {request.trial_id} ({request.tier})")
        
        # Build URLs (use your actual domain)
        success_url = f"https://regguard.com/checkout-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"https://regguard.com/free-trial"
        
        checkout_request = CheckoutRequest(
            trial_id=request.trial_id,
            tier=request.tier,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        result = await create_checkout_session(checkout_request)
        
        logger.info(f"✅ Checkout session created: {result['session_id']}")
        
        return CheckoutResponse(
            session_id=result['session_id'],
            checkout_url=result['checkout_url'],
        )
        
    except Exception as e:
        logger.error(f"❌ Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/stripe")
async def handle_stripe_webhook(request: Request) -> Dict[str, Any]:
    '''
    Handle Stripe webhook events
    
    Handles:
    - payment_intent.succeeded → Generate PDFs + send email
    - payment_intent.payment_failed → Update order status
    - charge.refunded → Process refund
    
    Required headers:
    - stripe-signature
    
    Note: Stripe will retry webhooks if not returning 200 quickly
    '''
    from stripe_integration import verify_webhook_signature, handle_webhook_event
    import stripe
    
    try:
        # Get raw body and signature
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            logger.error("❌ Missing stripe-signature header")
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # Verify signature
        if not verify_webhook_signature(payload, sig_header):
            logger.error("❌ Invalid webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Parse event
        event = await request.json()
        logger.info(f"🔔 Webhook: {event.get('type')}")
        
        # Handle event
        result = await handle_webhook_event(event)
        
        logger.info(f"✅ Webhook handled: {result}")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        # Still return 200 to prevent Stripe retries
        return {"status": "error", "message": str(e)}


@app.post("/generate-pdfs")
async def generate_pdfs(request: PDFGenerationRequest) -> Dict[str, Any]:
    '''
    Generate PDF package for a trial/order
    
    Generates:
    1. Research Memo PDF (environmental findings)
    2. Punch List PDF (action items)
    3. Permit Package PDF (state-specific)
    
    Args:
        request: PDFGenerationRequest with trial_id
    
    Returns:
        URLs to download PDFs
    
    Example:
        POST /generate-pdfs
        {
            "trial_id": "uuid-123",
            "tier": "premium"
        }
        
        Response:
        {
            "status": "success",
            "pdfs": {
                "research_memo": "https://cdn.regguard.com/pdfs/memo_123.pdf",
                "punch_list": "https://cdn.regguard.com/pdfs/punch_123.pdf",
                "permit_package": "https://cdn.regguard.com/pdfs/permits_123.pdf"
            },
            "expires_at": "2026-08-25T14:30:00Z"
        }
    '''
    from pdf_generator import generate_all_pdfs
    from free_trial_service import get_trial_analysis
    
    try:
        logger.info(f"📄 Generating PDFs for trial {request.trial_id}")
        
        # Fetch analysis data from database
        analysis_data = await get_trial_analysis(request.trial_id)
        
        if not analysis_data:
            logger.error(f"❌ No analysis found for trial {request.trial_id}")
            raise HTTPException(status_code=404, detail="Trial not found")
        
        # Generate PDFs
        pdf_paths = await generate_all_pdfs(analysis_data)
        
        # Upload to S3/CDN (in production)
        pdf_urls = {
            "research_memo": f"https://cdn.regguard.com/{pdf_paths['research_memo'].split('/')[-1]}",
            "punch_list": f"https://cdn.regguard.com/{pdf_paths['punch_list'].split('/')[-1]}",
            "permit_package": f"https://cdn.regguard.com/{pdf_paths['permit_package'].split('/')[-1]}",
        }
        
        logger.info(f"✅ PDFs generated: {pdf_urls}")
        
        return {
            "status": "success",
            "pdfs": pdf_urls,
            "expires_at": "2026-08-25T14:30:00Z",  # 30 days from now
        }
        
    except Exception as e:
        logger.error(f"❌ PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/{order_id}")
async def get_order(order_id: str) -> OrderResponse:
    '''
    Get order details including PDF links
    
    Args:
        order_id: Order ID to retrieve
    
    Returns:
        Order details with PDF download links
    '''
    try:
        logger.info(f"📋 Fetching order {order_id}")
        
        # Fetch from database
        # order = await fetch_order_from_db(order_id)
        
        # In production: return actual order data
        return OrderResponse(
            order_id=order_id,
            trial_id="uuid-123",
            tier="premium",
            status="completed",
            created_at="2026-07-25T14:30:00Z",
            pdf_urls={
                "research_memo": "https://cdn.regguard.com/memo_123.pdf",
                "punch_list": "https://cdn.regguard.com/punch_123.pdf",
                "permit_package": "https://cdn.regguard.com/permits_123.pdf",
            },
        )
        
    except Exception as e:
        logger.error(f"❌ Order fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders")
async def list_orders(email: str) -> Dict[str, Any]:
    '''
    List all orders for a user
    
    Args:
        email: User email to filter orders
    
    Returns:
        List of orders
    
    Example:
        GET /orders?email=user@example.com
    '''
    try:
        logger.info(f"📋 Listing orders for {email}")
        
        # Fetch from database
        # orders = await fetch_user_orders(email)
        
        # In production: return actual orders
        return {
            "user_email": email,
            "orders": [
                {
                    "order_id": "order_123",
                    "trial_id": "uuid-123",
                    "tier": "premium",
                    "status": "completed",
                    "created_at": "2026-07-25T14:30:00Z",
                    "amount": 15000,
                }
            ],
        }
        
    except Exception as e:
        logger.error(f"❌ Orders list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/set-tier")
async def set_user_tier(email: str, tier: str) -> Dict[str, Any]:
    '''
    Set user's tier (admin endpoint)
    
    Args:
        email: User email
        tier: Tier to set ("free", "premium", "enterprise")
    '''
    from stripe_integration import set_user_tier
    
    try:
        logger.info(f"👤 Setting tier for {email}: {tier}")
        
        await set_user_tier(email, tier)
        
        return {
            "status": "success",
            "user_email": email,
            "tier": tier,
        }
        
    except Exception as e:
        logger.error(f"❌ Tier setting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
"""

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

"""
Add these to your .env file:

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# S3/CDN (for storing PDFs)
S3_BUCKET_NAME=regguard-pdfs
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...

# Email
RESEND_API_KEY=...
RESEND_FROM_EMAIL=support@regguardagent.com
"""

# ============================================================================
# DATABASE MIGRATIONS (SQL)
# ============================================================================

"""
Run these SQL migrations in Supabase:

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    trial_id UUID REFERENCES free_trials(id),
    tier TEXT NOT NULL CHECK (tier IN ('free', 'premium', 'enterprise')),
    amount_cents INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    stripe_session_id TEXT,
    stripe_payment_intent_id TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_email ON orders(user_email);
CREATE INDEX idx_orders_trial_id ON orders(trial_id);
CREATE INDEX idx_orders_status ON orders(status);

-- PDF links table
CREATE TABLE IF NOT EXISTS pdf_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    pdf_type TEXT NOT NULL CHECK (pdf_type IN ('research_memo', 'punch_list', 'permits')),
    file_path TEXT NOT NULL,
    s3_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_pdf_links_order ON pdf_links(order_id);
CREATE INDEX idx_pdf_links_expires ON pdf_links(expires_at);

-- Premium tiers table
CREATE TABLE IF NOT EXISTS premium_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT UNIQUE NOT NULL,
    tier TEXT NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'premium', 'enterprise')),
    subscription_status TEXT,
    renewal_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tiers_email ON premium_tiers(user_email);
CREATE INDEX idx_tiers_tier ON premium_tiers(tier);
"""
