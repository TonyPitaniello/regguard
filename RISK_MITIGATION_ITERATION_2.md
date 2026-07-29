# Risk Mitigation Framework - ITERATION 2
## New Risks Emerging from Iteration 1 Fixes

**Date**: July 28, 2026  
**Iteration**: 2 of 4  
**Confidence Level After Iteration 1**: 65%  
**Target**: 75%+ after Iteration 2

---

## EXECUTIVE SUMMARY - ITERATION 2

Iteration 1 fixes introduced **complexity** and **new operational dependencies**:

1. **Redis dependency** (fix for T-004) → new failure mode: Redis crashes
2. **Webhook autoscaling** (fix for T-001) → new failure mode: autoscaling misconfigured
3. **Sponsor tracking server-side** (fix for B-004) → new failure mode: tracking code leaks/is wrong
4. **Contractor hiring** (fix for O-004) → new failure mode: contractor underperforms/leaves
5. **Pricing A/B test** (fix for B-001) → new failure mode: A/B framework buggy, winner unclear
6. **JWT refresh tokens** (fix for T-003) → new failure mode: refresh token rotation has race conditions
7. **SendGrid integration** (fix for B-002) → new failure mode: SendGrid API changes, quota issues
8. **Customer diversification** (fix for B-008) → new failure mode: new customers cost too much to acquire

Identified **22 new risks** from these fixes. Top 10 most concerning premortem failures included.

---

## NEW RISKS FROM ITERATION 1 FIXES

### REDIS DEPENDENCY RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|-----------|
| I2-T-001 | Redis pod crashes, rate limiting fails silently | High | Critical | Add Redis health check every 10s, fail fast with 503 if Redis down, implement in-memory fallback (rate limit 50 IPs max) |
| I2-T-002 | Redis memory exhaustion (key expiry not working) | Medium | Important | Set Redis maxmemory policy to evict oldest keys first, monitor memory usage, alert at 80% |
| I2-T-003 | Redis replication lag (multi-region deployment) | Medium | Important | Use Redis Cluster instead of single instance, accept <100ms replication lag, document consistency guarantees |
| I2-T-004 | Rate limit keys accumulate forever (memory leak) | Medium | Important | Set TTL on rate limit keys (2 hours), use Redis pipeline for batch cleanup |

### WEBHOOK AUTOSCALING RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|-----------|
| I2-O-001 | Autoscaling triggers incorrectly (spins up 100 workers for blip) | High | Important | Add cooldown period (5 min between scaling events), set max workers to 10 (not unlimited) |
| I2-O-002 | Webhook worker startup is slow (takes 60s), scaling ineffective | Medium | Important | Pre-warm 2 workers always, reduce startup time to <10s via lazy imports |
| I2-O-003 | Scaling down too fast (kills workers mid-request) | High | Important | Graceful shutdown: drain in-flight requests over 30s before terminating |
| I2-O-004 | Cost explosion: 10 workers × $50/month = $500/month extra | Medium | Important | Set budget alert in AWS, implement cost-per-event tracking, review scaling necessity quarterly |

### SPONSOR TRACKING RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|-----------|
| I2-B-001 | Sponsor code collision (user signs up with wrong sponsor code) | Medium | Important | Add email confirmation step: "You're being sponsored by Sponsor X, continue?", allow user to change sponsor |
| I2-B-002 | Sponsor codes leaked (10 sponsors share same code by mistake) | Medium | Important | Generate unique codes per sponsor, add validation before DB insert, add audit trail of code-to-sponsor mapping |
| I2-B-003 | Sponsor tracking retroactively incomplete (historical data missing) | High | Important | For MVP: accept that pre-launch data won't have sponsors, document data cutoff date in dashboard |
| I2-B-004 | Manual sponsor management (codes) becomes operational burden | Medium | Important | Build sponsor admin dashboard to self-service generate/track codes |

### CONTRACTOR HIRING RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|-----------|
| I2-O-005 | Contractor underperforms (3x slower than estimate) | High | Important | Hire for 4 weeks trial with performance milestones (week 2 = X features done), can terminate early |
| I2-O-006 | Contractor costs 2x budget ($15K/month instead of $7.5K) | Medium | Important | Set firm rate in contract, get recruiter to vet technical skills first, negotiate fixed monthly price |
| I2-O-007 | Contractor leaves after 4 weeks, continuity lost | Medium | Important | Require detailed documentation from day 1, pair with internal engineer 50% of time, knowledge transfer plan |
| I2-O-008 | Remote contractor timezone issues (8+ hour gap) | Medium | Important | Set core overlap hours (4 hours/day minimum), daily async standups via Slack |

### A/B TESTING RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|---------|
| I2-B-005 | A/B test framework has bugs (conversion events miscounted) | High | Important | Unit test A/B framework with synthetic data, spot-check 1% of events manually |
| I2-B-006 | Winner inconclusive (Tier A: 12%, Tier B: 11%, no clear winner) | Medium | Important | Accept 80% confidence threshold, declare winner even if slight edge, set decision deadline (2 weeks max) |
| I2-B-007 | A/B test runs forever (never enough sample size) | Medium | Important | Set minimum sample size (100 conversions = 2-week decision), stop test after 2 weeks regardless |
| I2-B-008 | Cannibalization: higher pricing tier cannibalizes lower tier | Medium | Important | Segment A/B by user type (new free users only, not existing paying customers) |

### JWT REFRESH TOKEN RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|-----------|
| I2-T-005 | Race condition: two refresh requests issued simultaneously, both old tokens accepted | High | Important | Add unique `refresh_token_id` to track issue, allow only ONE active refresh token per user, reject old tokens immediately |
| I2-T-006 | Refresh token database grows unbounded (no cleanup) | Medium | Important | Delete used refresh tokens after 24 hours, set automatic purge job |
| I2-T-007 | Refresh token secret exposed (hardcoded in code) | Low | Critical | Always use SUPABASE_JWT_SECRET from env, never hardcode, audit codebase for hardcoded secrets |
| I2-T-008 | Token rotation breaks mobile app (offline users can't refresh) | Medium | Important | Allow grace period: old refresh token valid for 5 min after new one issued |

### SENDGRID INTEGRATION RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|-----------|
| I2-B-009 | SendGrid quota hit (100K emails/month for free tier), suddenly can't send | High | Important | Set alert at 80% quota usage, have backup SMTP provider (Mailgun) configured, upgrade plan if needed |
| I2-B-010 | SendGrid API changes (endpoint deprecated), email sending breaks | Medium | Important | Monitor SendGrid changelog, add integration tests with live API, keep SDK updated |
| I2-B-011 | Email unsubscribe list grows too fast (>10% unsubscribe rate) | Medium | Important | Analyze unsubscribe reasons, resend confirmation email, adjust email frequency |

### CUSTOMER DIVERSIFICATION RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|-----------|
| I2-B-011 | Sales efforts to acquire new customers cost $50K, yield only $100K revenue (2:1 ROI) | High | Important | Measure CAC per segment, target CAC <$3K (works only if LTV >$10K), adjust target segments |
| I2-B-012 | New SMB customers churn 80% after 3 months (not viable segment) | High | Important | Run cohort analysis monthly, identify high-churn segments early, stop targeting that segment |
| I2-B-013 | Sales team isn't hired (hiring takes 3 months), diversification delayed | Medium | Important | Start recruiting immediately, offer generous referral bonus to accelerate hiring |

---

## ITERATION 2 PREMORTEM: TOP 10 FAILURE MODES

| Rank | New Risk | Mitigation from Iter 1 Fix | Premortem Failure | Risk Score | Likelihood | Impact |
|------|---|---|---|---|---|---|
| 1 | I2-T-001 | Redis health check | Health check fails too late (5 min after crash), rate limiting bypassed | 85 | High | Critical |
| 2 | I2-O-001 | Autoscaling cooldown | Cooldown period too long (5 min), queue backs up during cooldown | 80 | High | Important |
| 3 | I2-B-003 | Sponsor code historical data | Historical sponsors = 0, launch looks like new tier flopped | 80 | High | Important |
| 4 | I2-O-005 | Contractor trial period | Contractor passes trial but still underperforms in production | 75 | High | Important |
| 5 | I2-B-005 | A/B test framework | Conversion event mismatch: frontend counts diff than backend | 75 | High | Important |
| 6 | I2-T-005 | JWT refresh race condition | Race condition happens in production, 100 concurrent refresh requests fail | 75 | High | Important |
| 7 | I2-B-009 | SendGrid quota | Quota hit on Day 1 of retention email campaign, emails not sent | 75 | High | Important |
| 8 | I2-B-011 | SMB customer churn | New SMB tier launched, 80% churn, credibility damaged, market perception negative | 75 | High | Important |
| 9 | I2-T-003 | Redis replication lag | Multi-region deployment, rate limit not replicated to secondary, requests bypass limit | 70 | Medium | Important |
| 10 | I2-O-004 | Worker scaling costs | Costs spiral to $5K/month, board questions scaling strategy | 65 | Medium | Important |

**Total Iteration 2 Premortem Risk**: 755 / 10 = **75.5 avg** (HIGH, same as Iter 1)

---

## FIXES FOR ITERATION 2 TOP 10

| Rank | Risk | Fix | Owner | Timeline |
|------|------|-----|-------|----------|
| 1 | I2-T-001: Redis health check too slow | Reduce health check interval to 5 seconds, use circuit breaker pattern (fail after 2 consecutive failures = immediate 503), pre-warm rate limit cache on startup | Backend | Phase 3 Week 1 |
| 2 | I2-O-001: Autoscaling cooldown too long | Reduce cooldown to 2 minutes, enable prediction: scale preemptively if queue >200 for 30s (not 500 for 5 min) | DevOps | Phase 3 Week 1 |
| 3 | I2-B-003: Historical sponsor data missing | Accept that sponsor ROI dashboard has data cutoff (July 28, 2026), document in UI, provide estimated historical conversions | Product | Phase 3 Week 2 |
| 4 | I2-O-005: Contractor underperformance | Add weekly code review checkpoint (Week 1-4), assign dedicated tech lead, have performance review at end of Week 2 (not Week 4) | Leadership | Immediate |
| 5 | I2-B-005: A/B test conversion mismatch | Implement event deduplication: frontend + backend both log conversion, reconcile daily, use backend count as source of truth | Backend + Frontend | Phase 3 Week 1 |
| 6 | I2-T-005: JWT refresh race condition | Implement optimistic locking: refresh token includes version number, reject old version if newer exists, allow 2-minute grace period | Backend | Phase 3 Week 1 |
| 7 | I2-B-009: SendGrid quota hit | Pre-purchase 500K emails/month (not free tier), set alert at 400K usage, add Mailgun as fallback (send 10% of non-critical emails via Mailgun) | Product + Backend | Phase 3 Week 1 |
| 8 | I2-B-011: SMB churn | Before launch, run closed beta with 5 SMB customers, measure churn after 4 weeks, don't go public until retention >50% | Product | Phase 3 Week 0.5 |
| 9 | I2-T-003: Redis replication lag | DON'T implement Redis Cluster for MVP (complexity), instead: use single Redis instance, accept <100ms rate limit drift, document trade-off | Backend | Phase 3 Week 2 |
| 10 | I2-O-004: Scaling cost explosion | Add cost monitoring: track $ per webhook processed, set budget cap ($500/month), alert if exceeding, review scaling approach monthly | DevOps | Phase 3 Week 1 |

---

## ITERATION 2 CONFIDENCE ASSESSMENT

| Component | Pre-Iteration 2 | Post-Iteration 2 | Gap |
|-----------|---|---|---|
| Technical | 45 avg | 35 avg | ✅ 22% improvement |
| Business | 50 avg | 40 avg | ✅ 20% improvement |
| Operational | 40 avg | 30 avg | ✅ 25% improvement |
| Market | 60 avg | 55 avg | ✅ 8% improvement |
| UX | 50 avg | 45 avg | ✅ 10% improvement |

**Overall Confidence After Iteration 2 Fixes**: 72% ← Up from 65%

---

## RESIDUAL RISKS AFTER ITERATION 2

| Risk | Mitigation |
|------|-----------|
| Redis single point of failure still exists for MVP | Accept for MVP, implement multi-region in Phase 4 |
| Contractor still may leave mid-project | Accept risk, document continuity, hire 2nd contractor if needed |
| A/B test decision still subjective (80% confidence threshold) | Implement decision rule upfront, commit to deadline |
| SendGrid fallback (Mailgun) adds complexity | Document as Phase 4 enhancement |

---

## CONCLUSION - ITERATION 2

After Iteration 2 fixes, confidence improved from **65% → 72%**. Still below **75% target**.

New emergent risks have mostly **medium** likelihood + **important** impact (not critical).

**Decision**: Execute **Iteration 3** focusing on:
1. Team execution risks (contractor, team bandwidth)
2. Data quality risks (A/B test accuracy, sponsor tracking accuracy)
3. Market validation risks (SMB churn, sponsor ROI)

See `RISK_MITIGATION_ITERATION_3.md` for Iteration 3.
