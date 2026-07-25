# Phase 2 Enterprise Implementation Plan

**Scope**: Full production-grade RegGuard with PDFs, permits, premium tier  
**Timeline**: 3 weeks (aggressive but achievable)  
**Deliverables**: Professional product ready for paid sales

---

## 🎯 Phase 2 Overview

### What We're Building

**Free Tier** (Free Trial):
- Text research memo via email
- Punch list preview (top 5 items)
- Results page display
- No credit card required

**Premium Tier** ($15,000):
- Professional PDF reports (branded)
- Complete punch list (all items, formatted)
- Permit application packages (state-specific, pre-filled)
- Same-day delivery via email
- Access to results portal for 30 days

**Enterprise Tier** ($60K/year):
- Everything in Premium
- Plus annual monitoring
- Plus 2 additional reports
- Plus white-label option

---

## 📋 Implementation Breakdown

### Week 1: PDF Generation (4-5 days)

**Goals**:
- Research memo PDF (branded)
- Punch list PDF (formatted table)
- Permit packages PDF (state-specific pre-filled)

**Components to Build**:

1. **`pdf_generator.py`** (350+ lines)
   - PDF template engine
   - Branding/styling (logos, headers, footers)
   - 3 PDF types
   - Error handling

2. **`branding_config.py`** (100+ lines)
   - Colors, fonts, logos
   - Header/footer templates
   - Table styles

3. **`permit_templates.py`** (200+ lines)
   - Texas templates (Plano, Dallas, Houston, Austin, San Antonio)
   - Generic template for other states
   - Field mappings

4. **Backend endpoint**: `/generate-pdfs`
   - Takes analysis data
   - Generates 3 PDFs
   - Returns S3/cloud URLs

5. **Frontend**: Premium checkout → Trigger PDF generation

**Libraries**: `fpdf2` or `ReportLab` (already in requirements)

---

### Week 2: Permit Packages & State Logic (4-5 days)

**Goals**:
- Auto-generate permit packages for top 5 states
- State-specific requirements and timelines
- Pre-fill forms with project data

**Components to Build**:

1. **`permit_packages.py`** (400+ lines)
   - Permit templates by state
   - Form field mapping
   - Auto-fill logic
   - State-specific requirements

2. **`state_requirements.py`** (300+ lines)
   - Texas requirements
   - California (if available)
   - New York (if available)
   - Others as needed
   - Utility-specific timelines

3. **`permit_generator.py`** (200+ lines)
   - Takes analysis data
   - Generates permit packages
   - Returns formatted PDFs

4. **Database migrations**:
   - Premium tier tracking
   - PDF generation status
   - Permit package cache

---

### Week 3: Premium Tier & Stripe (4-5 days)

**Goals**:
- Stripe payment integration ($15K checkout)
- Premium tier gating
- Full tier differentiation
- Order fulfillment pipeline

**Components to Build**:

1. **`stripe_integration.py`** (200+ lines)
   - Checkout session creation
   - Webhook handling
   - Order creation
   - PDF delivery automation

2. **Backend endpoints**:
   - `/checkout` - Create Stripe session
   - `/webhook/stripe` - Handle payment events
   - `/orders` - List user orders
   - `/download-pdf/{pdf_id}` - PDF download

3. **Frontend pages**:
   - Results page with upgrade CTA
   - Checkout success page
   - Order history page
   - Download portal

4. **Database changes**:
   - Orders table
   - PDF links table
   - Premium tier tracking
   - Subscription management

5. **Email automation**:
   - Order confirmation
   - PDF delivery email (with links + attachments)
   - Invoice generation

---

## 🛠️ Technology Stack

**PDF Generation**:
- `fpdf2` (already in requirements) or `reportlab`
- For complex layouts: `weasyprint` (HTML → PDF)

**State/Permit Data**:
- Python dataclasses for structure
- JSON for flexibility
- Database for caching

**Payment**:
- Stripe API
- Webhook signature verification
- Database for order tracking

**Storage**:
- S3 (for PDFs) or Supabase storage
- Email attachments via Resend

---

## 📊 Implementation Order (Priority)

**Priority 1 (Days 1-3)**: 
1. Basic PDF generation (research memo)
2. Texas permit templates
3. Stripe checkout endpoint

**Priority 2 (Days 4-7)**:
1. Punch list PDF
2. Permit package PDF generation
3. Webhook handling for payments

**Priority 3 (Days 8-10)**:
1. Frontend tier differentiation
2. Download portal
3. Order history

**Priority 4 (Days 11-15)**:
1. Additional states (CA, NY, etc.)
2. Advanced logic per state
3. Email automation

**Priority 5 (Days 16-21)**:
1. Testing and QA
2. Performance optimization
3. Documentation and launch prep

---

## 💻 Code Blocks to Build

### Block 1: PDF Generator (Day 1)
```python
# backend/pdf_generator.py
from fpdf import FPDF
from dataclasses import dataclass
from typing import List, Dict, Any
import os

class ResearchMemoPDF(FPDF):
    """Generate branded research memo PDF"""
    
class PunchListPDF(FPDF):
    """Generate punch list PDF with table"""
    
class PermitPackagePDF(FPDF):
    """Generate pre-filled permit application PDF"""

def generate_all_pdfs(analysis_data: Dict) -> Dict[str, str]:
    """Generate memo, punch list, and permit PDFs"""
```

### Block 2: Permit Templates (Days 2-3)
```python
# backend/permit_templates.py
from dataclasses import dataclass

@dataclass
class PermitTemplate:
    state: str
    county: str
    municipality: str
    forms_required: List[str]
    estimated_cost: float
    estimated_timeline: str
    key_requirements: List[str]

# Texas templates
PLANO_PERMIT = PermitTemplate(...)
DALLAS_PERMIT = PermitTemplate(...)
# ... more cities

# Auto-fill mappings
FIELD_MAPPINGS = {
    "project_name": "analysis.project_info.address",
    "site_coordinates": "analysis.project_info.coordinates",
    ...
}
```

### Block 3: Stripe Integration (Days 4-5)
```python
# backend/stripe_integration.py
import stripe
from pydantic import BaseModel

class CheckoutSession(BaseModel):
    trial_id: str
    tier: str  # "premium" or "enterprise"

@app.post("/checkout")
async def create_checkout_session(session: CheckoutSession):
    """Create Stripe checkout session"""
    
@app.post("/webhook/stripe")
async def handle_stripe_webhook(request: Request):
    """Handle payment_intent.succeeded event"""
```

### Block 4: Premium Tier Gating (Days 6-7)
```python
# backend/tier_service.py
async def get_user_tier(user_id: str) -> str:
    """Get user's tier: free, premium, or enterprise"""

async def can_access_premium_feature(user_id: str, feature: str) -> bool:
    """Check if user can access feature"""

# Features map
FEATURES_BY_TIER = {
    "free": ["memo", "punch_list_preview"],
    "premium": ["memo", "full_punch_list", "pdfs", "permits"],
    "enterprise": ["everything", "monitoring", "white_label"],
}
```

### Block 5: Frontend Premium Page (Days 8-9)
```typescript
// frontend/src/pages/PremiumCheckoutPage.tsx
// Stripe Elements integration
// Checkout flow
// Success/error handling
```

---

## 📦 Database Schema Changes

### New Tables

```sql
-- Orders table
CREATE TABLE orders (
  id uuid PRIMARY KEY,
  user_email TEXT,
  trial_id uuid,
  tier TEXT,
  amount_cents INTEGER,
  status TEXT,
  created_at TIMESTAMP,
  stripe_session_id TEXT,
  stripe_payment_intent_id TEXT
);

-- PDF links table
CREATE TABLE pdf_links (
  id uuid PRIMARY KEY,
  order_id uuid,
  pdf_type TEXT, -- "memo", "punch_list", "permits"
  file_path TEXT,
  s3_url TEXT,
  created_at TIMESTAMP,
  expires_at TIMESTAMP
);

-- Premium tier table
CREATE TABLE premium_tiers (
  id uuid PRIMARY KEY,
  email TEXT,
  tier TEXT, -- "free", "premium", "enterprise"
  subscription_status TEXT,
  renewal_date DATE,
  created_at TIMESTAMP
);
```

---

## 🎯 Success Criteria for Phase 2

**PDF Generation**:
- [ ] Research memo PDF generates in < 5 seconds
- [ ] Punch list PDF shows all items formatted nicely
- [ ] Permit PDF pre-fills with correct data
- [ ] PDFs have branding (logo, colors, headers)

**Permit Packages**:
- [ ] Texas permits auto-generate correctly
- [ ] Form fields pre-filled 95%+ accurately
- [ ] Multiple states supported
- [ ] State-specific requirements shown

**Premium Tier**:
- [ ] Free vs. Premium clearly differentiated
- [ ] Stripe checkout works end-to-end
- [ ] Payment triggers PDF generation
- [ ] PDFs emailed within 1 minute of payment
- [ ] Users can download PDFs for 30 days

**Production Readiness**:
- [ ] No 500 errors in logs
- [ ] Payment processing 100% reliable
- [ ] Email delivery 99%+ success rate
- [ ] PDF generation 99%+ success rate
- [ ] Response times < 5 seconds for all endpoints

---

## 💡 Strategic Shortcuts

To complete in 3 weeks:

1. **Use existing libraries** (`fpdf2`, `stripe`, `resend`)
2. **Focus on top 5 states** (Texas first, add others if time)
3. **Template-based approach** (reusable templates, less custom code)
4. **Database caching** (cache generated PDFs for same data)
5. **Email automation** (Resend handles sending)
6. **Basic styling** (professional but not over-designed)

---

## 📈 Expected Outcome

By end of Phase 2:
- ✅ Professional, paid product ready
- ✅ $15K per transaction infrastructure
- ✅ Automatic order fulfillment
- ✅ Multi-state permit support
- ✅ Production-grade PDF delivery
- ✅ Competitive with existing solutions

**Revenue potential**: $225K-$900K/month (realistic)

---

## ⏱️ Timeline

**Week 1** (Jul 25-31): PDF generation + basic permits  
**Week 2** (Aug 1-7): Premium tier logic + state requirements  
**Week 3** (Aug 8-14): Stripe integration + testing + launch  

**Go-live date**: Mid-August 2026

---

**Status**: Plan complete, ready to implement 🚀
