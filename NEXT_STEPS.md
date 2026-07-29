# Phase 3: Next Steps for RegGuard SaaS Operationalization

## Overview

Phases 1-2 have established the foundation for multi-segment SaaS operations:
- ✅ Unified payment pipeline (Stripe checkout, webhooks, orders)
- ✅ Real authentication (Supabase JWT with RBAC)
- ✅ Database schema (orders + profiles)
- ✅ Frontend route updates and SignupPage redirect

This document outlines the remaining work for Phase 3 to complete the operational SaaS system.

---

## Phase 3 Roadmap (Estimated: 40 hours)

### 3.1: Complete Authentication System (8 hours)

#### 3.1.1 Backend Auth Endpoints

Implement in `backend/main.py`:

```python
@app.post("/auth/signup")
async def signup(email: str, password: str, company_name: str):
    """Create Supabase auth user + profile"""
    # 1. Call supabase.auth.sign_up(email, password)
    # 2. Create profile record with tier='free', segment='contractor'
    # 3. Return checkout_url for free trial
    pass

@app.get("/auth/me")
@require_auth
async def get_profile(request: Request):
    """Return authenticated user's profile"""
    user = request.state.user
    # Query profiles table for user.id
    # Return tier, segment, company_name, trial_expires_at
    pass

@app.post("/auth/logout")
@require_auth
async def logout(request: Request):
    """Invalidate user's session"""
    # In stateless JWT: client just deletes token
    # Optional: add token blacklist if needed
    pass

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Generate new JWT from refresh token"""
    # Implement refresh token logic
    pass
```

#### 3.1.2 Frontend Auth Context

Create `frontend/src/context/AuthContext.tsx`:

```typescript
import { createContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import axios from 'axios';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await axios.get('/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
        setProfile(response.data);
        setToken(token);
      } catch (err) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const login = async (email: string, password: string) => {
    const { data } = await supabase.auth.signInWithPassword({ email, password });
    const token = data.session.access_token;
    localStorage.setItem('token', token);
    setToken(token);
    setUser(data.user);
    return data.user;
  };

  const signup = async (email: string, password: string, company_name: string) => {
    const { data } = await supabase.auth.signUp({ email, password });
    const token = data.session.access_token;
    localStorage.setItem('token', token);
    setToken(token);
    setUser(data.user);
    // Fetch checkout URL from backend
    return { user: data.user, token };
  };

  const logout = async () => {
    await supabase.auth.signOut();
    localStorage.removeItem('token');
    setUser(null);
    setProfile(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, profile, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

#### 3.1.3 Add Login Page

Create `frontend/src/pages/LoginPage.tsx`:

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 px-4 py-16">
      <div className="max-w-md mx-auto">
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 rounded-3xl p-8">
          <h1 className="text-3xl font-black text-white mb-2">Log In</h1>
          <p className="text-gray-400 mb-8">Access your RegGuard account</p>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full px-4 py-2 bg-slate-900/50 border border-purple-500/20 rounded-lg text-white focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2 bg-slate-900/50 border border-purple-500/20 rounded-lg text-white focus:border-purple-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Log In'}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-purple-500/10">
            <p className="text-center text-sm text-gray-400">
              Don't have an account? <a href="/signup" className="text-purple-400 hover:text-purple-300">Sign up</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

#### 3.1.4 Update AppRouter with Auth Routes

```typescript
<Route path="/login" element={<LoginPage />} />
<Route path="/logout" element={<LogoutPage />} />
```

---

### 3.2: Implement Tier Management (6 hours)

#### 3.2.1 Tier Upgrade/Downgrade Endpoints

```python
@app.post("/tier/upgrade")
@require_auth
async def upgrade_tier(request: Request, tier: str):
    """Upgrade user to higher tier"""
    user = request.state.user
    # 1. Validate tier is higher than current
    # 2. Create checkout session for tier upgrade
    # 3. Return checkout_url
    pass

@app.post("/tier/cancel-subscription")
@require_auth
async def cancel_subscription(request: Request):
    """Downgrade user back to free tier"""
    user = request.state.user
    # 1. Cancel Stripe subscription
    # 2. Update user tier to 'free'
    # 3. Return confirmation
    pass
```

#### 3.2.2 Tier Features Matrix

Update `backend/tier_features.py`:

```python
TIER_FEATURES = {
    "free": {
        "max_projects": 1,
        "max_reports": 5,
        "can_download_pdf": False,
        "can_export_csv": False,
        "support": "community",
    },
    "contractor_pro": {
        "max_projects": 50,
        "max_reports": 500,
        "can_download_pdf": True,
        "can_export_csv": True,
        "support": "email",
    },
    "ic_consultant": {
        "max_projects": 500,
        "max_reports": 5000,
        "can_download_pdf": True,
        "can_export_csv": True,
        "support": "phone",
    },
    "sponsor": {
        "max_projects": "unlimited",
        "max_reports": "unlimited",
        "can_download_pdf": True,
        "can_export_csv": True,
        "support": "dedicated",
    },
}

async def can_user_access_feature(user_id: str, feature: str) -> bool:
    """Check if user's tier allows feature"""
    profile = await get_user_profile(user_id)
    tier_features = TIER_FEATURES[profile.tier]
    return tier_features.get(feature, False)
```

#### 3.2.3 Feature Gate Middleware

```python
def require_feature(feature: str):
    """Decorator: Require user's tier supports feature"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = request.state.user
            if not await can_user_access_feature(user.id, feature):
                raise HTTPException(status_code=403, detail="Feature not available in your tier")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

### 3.3: Customer Portal (10 hours)

#### 3.3.1 Billing Dashboard

Create `frontend/src/pages/BillingPage.tsx`:

- Current tier display
- Payment history
- Upcoming renewal date
- Upgrade/downgrade buttons
- Download invoices

#### 3.3.2 Order History with Pagination

Update `frontend/src/pages/OrdersPage.tsx`:

```typescript
export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders(page);
  }, [page]);

  const fetchOrders = async (pageNum: number) => {
    const response = await axios.get('/orders', {
      params: { page: pageNum, limit: 10 },
      headers: { Authorization: `Bearer ${token}` }
    });
    setOrders(response.data.orders);
  };

  return (
    <div>
      <h1>Order History</h1>
      <table>
        <tr>
          <th>Date</th>
          <th>Tier</th>
          <th>Amount</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
        {orders.map(order => (
          <tr key={order.id}>
            <td>{new Date(order.created_at).toLocaleDateString()}</td>
            <td>{order.tier}</td>
            <td>${(order.amount / 100).toFixed(2)}</td>
            <td>{order.status}</td>
            <td><a href={`/order/${order.id}`}>Details</a></td>
          </tr>
        ))}
      </table>
      <Pagination page={page} onPageChange={setPage} />
    </div>
  );
}
```

#### 3.3.3 Invoice Generation

Create `backend/invoice_service.py`:

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

async def generate_invoice_pdf(order_id: str) -> bytes:
    """Generate PDF invoice for order"""
    order = await get_order(order_id)
    
    # Create PDF
    pdf_path = f"/tmp/invoice_{order_id}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    c.drawString(100, 750, "RegGuard Invoice")
    c.drawString(100, 730, f"Invoice #{order_id}")
    c.drawString(100, 710, f"Date: {datetime.now().strftime('%m/%d/%Y')}")
    
    # Add order details
    c.drawString(100, 650, f"Tier: {order.tier}")
    c.drawString(100, 630, f"Amount: ${order.amount/100:.2f}")
    c.drawString(100, 610, f"Status: {order.status}")
    
    c.save()
    
    with open(pdf_path, 'rb') as f:
        return f.read()

@app.get("/order/{order_id}/invoice")
@require_auth
async def download_invoice(request: Request, order_id: str):
    """Download order invoice as PDF"""
    user = request.state.user
    order = await get_order(order_id)
    
    # Verify user owns order
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    pdf = await generate_invoice_pdf(order_id)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{order_id}.pdf"}
    )
```

---

### 3.4: Usage Analytics (8 hours)

#### 3.4.1 Track Feature Usage

```python
# Add to middleware
async def track_usage(request: Request, user_id: str, feature: str, units: int = 1):
    """Track feature usage for billing"""
    # Insert into usage_metrics table
    # Used for tracking reports generated, PDFs downloaded, etc.
    pass
```

#### 3.4.2 Usage Dashboard

Create `frontend/src/pages/AnalyticsPage.tsx`:

- Reports generated this month
- API calls used
- Storage used
- Users created
- Exports performed

#### 3.4.3 Analytics Endpoints

```python
@app.get("/analytics/usage")
@require_auth
async def get_usage_analytics(request: Request, period: str = "month"):
    """Get user's feature usage stats"""
    user = request.state.user
    # Query usage_metrics table
    # Return aggregated usage by feature
    pass

@app.get("/analytics/dashboard")
@require_tier("sponsor_admin", "partner_admin")
async def get_dashboard_analytics():
    """Admin dashboard with all-user metrics"""
    # Return total revenue, active users, churn, etc.
    pass
```

---

### 3.5: Improved Error Handling (4 hours)

#### 3.5.1 Custom Error Codes

```python
class RegGuardException(Exception):
    """Base exception for RegGuard"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

class StripeError(RegGuardException):
    """Stripe-related errors"""
    pass

class AuthenticationError(RegGuardException):
    """Auth-related errors"""
    pass

class InsufficientTierError(RegGuardException):
    """Tier permission errors"""
    pass
```

#### 3.5.2 Global Exception Handler

```python
@app.exception_handler(RegGuardException)
async def regguard_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "request_id": request.headers.get("x-request-id")
        }
    )
```

---

### 3.6: Testing & Documentation (4 hours)

#### 3.6.1 Integration Tests

```bash
pytest backend/tests/test_auth_endpoints.py
pytest backend/tests/test_tier_management.py
pytest backend/tests/test_analytics.py
```

#### 3.6.2 End-to-End Tests

```typescript
// cypress/e2e/payment-flow.cy.ts
describe('Payment Flow', () => {
  it('should complete signup → checkout → payment → dashboard', () => {
    // Full flow test
  });
});
```

---

## Implementation Priority

### Critical Path (Days 1-5)
1. Backend auth endpoints (signup, me, logout)
2. Frontend AuthContext + LoginPage
3. Tier upgrade/downgrade endpoints
4. Basic billing page

### High Priority (Days 5-8)
5. Invoice generation
6. Usage tracking + analytics endpoints
7. Improved error handling
8. E2E tests

### Polish (Days 8-10)
9. Email notifications
10. Documentation updates
11. Performance optimization
12. Security audit

---

## Estimated Timeline

- **Phase 3.1** (Auth): 8 hours
- **Phase 3.2** (Tier Management): 6 hours
- **Phase 3.3** (Customer Portal): 10 hours
- **Phase 3.4** (Analytics): 8 hours
- **Phase 3.5** (Error Handling): 4 hours
- **Phase 3.6** (Testing & Docs): 4 hours

**Total**: ~40 hours = 1 week at full-time pace

---

## Success Criteria for Phase 3

- [ ] Users can sign up, log in, and access dashboard
- [ ] Users can upgrade/downgrade tiers
- [ ] Billing page shows order history + upcoming renewal
- [ ] Invoice generation working
- [ ] Usage tracking and analytics operational
- [ ] All tests passing (>20 tests)
- [ ] Error handling comprehensive
- [ ] Documentation complete
- [ ] Ready for beta customer launch

---

## Customer Segments Ready for Beta

1. **Contractors** (free tier → contractor_pro)
2. **IC Consultants** (free tier → ic_consultant)
3. **Sponsors** (free tier → sponsor_admin)
4. **Partners** (custom via partner_admin)

---

## References

- [Stripe Subscriptions](https://stripe.com/docs/billing/subscriptions/overview)
- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Context API](https://react.dev/reference/react/useContext)

---

**Status**: Ready for Phase 3 planning
**Estimated Start**: Week of [DATE]
**Lead**: [TEAM MEMBER]
