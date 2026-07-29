# Risk Mitigation Framework - ITERATION 1
## RegGuard Multi-Segment SaaS

**Date**: July 28, 2026  
**Status**: Iteration 1 Complete (Identification + Mitigation)  
**Confidence Level**: 65% (after premortem: 42%)

---

## Executive Summary

This iteration identifies **38 risks** across 5 categories:
- **Technical Risks**: 10 identified, 8 HIGH+CRITICAL
- **Business Model Risks**: 8 identified, 5 HIGH+CRITICAL
- **Operational Risks**: 9 identified, 6 HIGH+CRITICAL
- **Market/Competitive Risks**: 6 identified, 3 HIGH+CRITICAL
- **UX Risks**: 5 identified, 2 HIGH+CRITICAL

**Total High+Critical Risks**: 24/38 (63%)

---

## RISK REGISTER - ITERATION 1

### 1. TECHNICAL RISKS

| Risk ID | Risk | Likelihood | Impact | Status | Mitigation Strategy |
|---------|------|-----------|--------|--------|---------------------|
| T-001 | Payment webhook timeout / Stripe API down | High | Critical | Unmitigated | Exponential backoff retry (3 retries over 10 min), queue to DLQ if max retries exceeded, alert on-call engineer after 3 failures |
| T-002 | Database integrity: CASCADE DELETE orphans orders | High | Critical | Unmitigated | Add orphan detection job (daily), add FK constraints with CASCADE checks, create backup before major migrations |
| T-003 | JWT token expiration edge cases (user mid-request when token expires) | Medium | Important | Unmitigated | Implement JWT refresh token rotation, add token expiry buffer (30s) in middleware, return 401 with refresh hint |
| T-004 | Rate limiting: No protection against brute force / DDoS | High | Critical | Unmitigated | Implement Redis rate limiter: 100 requests/min per IP, 50 requests/min per user, exponential backoff on violation |
| T-005 | Stripe webhook signature verification bypass (attacker spoofs webhook) | Medium | Critical | Unmitigated | Always verify Stripe signature using HMAC, never skip verification, log all failed verifications |
| T-006 | Database migration fails in production (rollback impossible) | Medium | Important | Unmitigated | Run migrations in staging first, create pre-migration backup, have documented rollback procedure, test 2x before prod |
| T-007 | Third-party API failures: Stripe rate limit exceeded | Medium | Important | Partially Mitigated | Add exponential backoff for Stripe calls, cache Stripe responses (60s), queue requests if rate limited |
| T-008 | Data persistence: Order created but webhook never received | High | Critical | Unmitigated | Implement order status reconciliation job (hourly), check Stripe API for payment status, update if mismatch |
| T-009 | Authentication bypass: Forged JWT tokens | Low | Critical | Unmitigated | Always verify JWT signature using SUPABASE_JWT_SECRET, validate claims (exp, iat, user_id), reject malformed tokens |
| T-010 | API performance under load: 10K concurrent users crashes server | Medium | Important | Unmitigated | Load testing needed, implement connection pooling for DB, add caching layer (Redis), implement horizontal scaling |

### 2. BUSINESS MODEL RISKS

| Risk ID | Risk | Likelihood | Impact | Status | Mitigation Strategy |
|---------|------|-----------|--------|--------|---------------------|
| B-001 | Contractor freemium conversion <2% | High | Critical | Unmitigated | Add in-app upgrade CTAs after 10 free lookups, feature teaser (blur premium reports), A/B test pricing ($99 vs $149 vs $199), email nurture sequence |
| B-002 | Pro tier churn rate >40% (within 3 months) | High | Critical | Unmitigated | Implement monthly email with usage stats + ROI metrics, add onboarding video, weekly check-in emails first month, offer 50% discount to at-risk users |
| B-003 | IC Consultant pricing mismatch ($5K want vs $15K ask) | High | Important | Unmitigated | Conduct market research with 10+ IC consultants, test pricing $5K-$20K range, offer custom pricing for high-volume users |
| B-004 | Sponsor ROI unclear (can't attribute conversions) | High | Critical | Unmitigated | Add conversion tracking pixel to sponsor links, provide monthly dashboard (CTR, CPC, conversion rate), offer 30-day ROI guarantee with refund |
| B-005 | Partner integration takes 6+ months (not 8 weeks) | Medium | Important | Unmitigated | Create integration quickstart guide, provide API SDK, offer integration support calls (weekly), set milestones at weeks 2, 4, 6 |
| B-006 | Free tier support burden explodes (100K free users → support tickets spike) | High | Important | Unmitigated | Implement self-serve knowledge base + chatbot for free tier, limit free tier support to async email (72h SLA), offer paid phone support only to Pro+ users |
| B-007 | PCI-DSS compliance costs more than expected (>$50K/yr) | Medium | Important | Unmitigated | Use Stripe for payment processing (reduces PCI scope), audit compliance quarterly, budget $30K-$50K for Year 1 |
| B-008 | Revenue concentration risk: One customer pays 30%+ of revenue | High | Important | Unmitigated | Diversify customer base, set contract terms to prevent unilateral termination, implement customer success program for top 10% |

### 3. OPERATIONAL RISKS

| Risk ID | Risk | Likelihood | Impact | Status | Mitigation Strategy |
|---------|------|-----------|--------|--------|---------------------|
| O-001 | Webhook backlog accumulates (order confirmations delayed 1+ hours) | High | Critical | Unmitigated | Monitor queue depth (alert if >1K), implement horizontal scaling for webhook workers, add DLQ (dead letter queue) for failed events |
| O-002 | Error handling gaps: Stripe errors not logged / surfaced | High | Important | Unmitigated | Add try-catch blocks to all Stripe calls, log errors with request ID + context, create error tracking dashboard in Sentry |
| O-003 | Monitoring insufficient: Don't notice issues until customer complains | High | Critical | Unmitigated | Set up Sentry for error tracking, implement monitoring for: webhook latency >5s, order failure rate >1%, JWT decode failures, database connection pool exhaustion |
| O-004 | Team doesn't have bandwidth for Phase 3-5 | Medium | Important | Unmitigated | Create prioritized roadmap, identify critical path items, hire contractor or contractor if needed, set realistic timelines |
| O-005 | Database backup strategy unclear (no disaster recovery) | Medium | Critical | Unmitigated | Enable Supabase automated daily backups, test restore process monthly, document backup retention (30 days), create runbook for disaster recovery |
| O-006 | Scaling to 100K users: Database queries slow down | Medium | Important | Unmitigated | Add database indexes on frequently queried columns (user_id, tier, created_at), profile query performance, implement caching layer |
| O-007 | Configuration management: Environment variables scattered / hardcoded | Medium | Important | Partially Mitigated | Use .env files, never commit secrets to git, use Supabase for secrets management, audit code for hardcoded values quarterly |
| O-008 | Deployments are manual / error-prone | Medium | Important | Unmitigated | Implement CI/CD pipeline (GitHub Actions), automate testing + deployment, create deployment runbook with checklist |
| O-009 | Incident response plan doesn't exist | Medium | Critical | Unmitigated | Create incident response playbook (who, what, when, how), define SLAs (critical = 1hr, high = 4hr), assign on-call rotation |

### 4. MARKET/COMPETITIVE RISKS

| Risk ID | Risk | Likelihood | Impact | Status | Mitigation Strategy |
|---------|------|-----------|--------|--------|---------------------|
| M-001 | Competitors launch similar product | Medium | Important | Unmitigated | Build moat: unique data sources, proprietary algorithms, customer relationships, first-mover advantage, brand loyalty |
| M-002 | Customers use free tier indefinitely (low conversion) | High | Important | Unmitigated | Implement usage-based features that prevent free tier adoption (max 5 reports/month), add premium feature teasers, email nurture |
| M-003 | Market adoption slower than expected | Medium | Important | Unmitigated | Adjust marketing strategy, increase customer acquisition budget, test different channels, measure CAC + LTV |
| M-004 | Regulatory changes (state regulations, PCI, privacy laws) | Low | Important | Unmitigated | Monitor compliance landscape, budget for legal review quarterly, implement privacy-by-default architecture |
| M-005 | Sponsor segment doesn't adopt (low market demand) | Medium | Important | Unmitigated | Conduct market validation with 20+ sponsor companies, test pricing/positioning, consider pivoting if <5% conversion |
| M-006 | Free tier abuse: Bot spam / scraping / crawling | Medium | Important | Unmitigated | Implement CAPTCHA on signup, rate limit API endpoints, monitor for suspicious patterns, add abuse detection ML model |

### 5. UX RISKS

| Risk ID | Risk | Likelihood | Impact | Status | Mitigation Strategy |
|---------|------|-----------|--------|--------|---------------------|
| U-001 | Signup flow too complex (conversion drops to <5%) | High | Important | Unmitigated | Simplify to 3 steps (email, password, company name), add progress indicator, make optional fields collapsible, A/B test |
| U-002 | Checkout flow confusing (abandoned carts >40%) | High | Important | Unmitigated | Show progress: "Step 1/3: Select Tier", "Step 2/3: Payment", "Step 3/3: Confirmation", reduce required fields, show price clearly |
| U-003 | Tier upgrade CTA not prominent enough | Medium | Important | Unmitigated | Add prominent banner when free tier limit exceeded, add upgrade button in multiple places (header, settings, after 10 reports) |
| U-004 | Sponsor banners too intrusive (free users leave) | Medium | Important | Unmitigated | Show sponsor banner only once per session, make dismissible (X button), test banner size/placement, measure CTR |
| U-005 | Error messages unhelpful (users contact support for simple issues) | Medium | Important | Unmitigated | Add specific error codes + human-readable messages, suggest fixes (e.g., "Payment failed: Card declined. Try a different card or contact support") |

---

## RISK HEAT MAP

```
CRITICAL Impact
    T-001 •  T-002 •  T-004 •  T-008 •  T-009 •
    B-001 •  B-002 •  B-004 •
    O-001 •  O-003 •  O-005 •  O-009 •

IMPORTANT Impact
    T-003 •  T-006 •  T-007 •  T-010 •
    B-003 •  B-005 •  B-006 •  B-007 •  B-008 •
    O-002 •  O-004 •  O-006 •  O-007 •  O-008 •
    M-001 •  M-002 •  M-003 •  M-004 •  M-005 •  M-006 •
    U-001 •  U-002 •  U-003 •  U-004 •  U-005 •

        Low        Medium       High
        ←── Likelihood ───→
```

---

## MITIGATION SUMMARY

**24 High+Critical Risks Identified**
**24 Mitigations Proposed**
**Status**: All high-risk items now have proposed mitigations

### Quick Mitigation Checklist

- [x] T-001: Webhook retry + DLQ
- [x] T-002: FK constraints + orphan detection
- [x] T-004: Redis rate limiter
- [x] T-008: Order reconciliation job
- [x] B-001: In-app CTAs + pricing A/B test
- [x] B-002: Usage metrics + retention emails
- [x] B-004: Conversion tracking + ROI dashboard
- [x] O-001: Queue monitoring + horizontal scaling
- [x] O-003: Sentry monitoring + alerting
- [x] O-009: Incident response playbook

---

## NEXT STEPS: PREMORTEM ANALYSIS

All mitigations proposed. Now running premortem to identify what could make these mitigations fail.

See `PREMORTEM_ITERATION_1.md` for detailed premortem analysis.
