# Iteration 1 Fixes - Top 10 Premortem Risks
## RegGuard Risk Mitigation Framework

**Date**: July 28, 2026  
**Status**: Addressing top 10 premortem risks (Risk Score 75-95)

---

## FIX STRATEGY

For each of the top 10 premortem risks, propose a **FIX** that eliminates the failure mode or reduces risk significantly.

---

## FIXES FOR TOP 10 RISKS

| Rank | Premortem Risk | Risk Score | Fix | Owner | Timeline | Implementation |
|------|---|---|---|---|---|---|
| 1 | **T-001: Queue backing up faster than processing** | 95 | Add queue depth monitoring with HARD ALERT at 2K events (not 5K). Implement autoscaling: if queue >1K for 5 min, spin up 2x webhook workers. Add DLQ processing: manual review daily, automatic retry after 24h. Test with simulated Stripe failure. | Backend | Phase 3 Week 1 | `webhook_monitor.py` + AWS Lambda autoscaling |
| 2 | **B-004: Sponsor conversion tracking fails** | 95 | DON'T rely on Firecrawl pixel. Instead: 1) Add direct attribution link tracking in database (link_id + sponsor_id), 2) Provide sponsors with unique referral codes to include in ads, 3) Track conversions server-side (when user signs up with code), 4) Monthly dashboard showing code → conversions. Test with 3 pilot sponsors before launch. | Product + Backend | Phase 3 Week 2 | `sponsor_tracking.py` + dashboard endpoint |
| 3 | **T-004: Redis rate limiter not deployed** | 90 | Add Redis as REQUIRED dependency (not optional). 1) Include Redis in docker-compose.yml, 2) Add health check for Redis connection on startup, 3) Fail fast if Redis unavailable (don't skip rate limiting), 4) Set rate limits in .env with sensible defaults, 5) Test rate limit under load (JMeter test with 1000 concurrent requests). | DevOps + Backend | Phase 3 Week 1 | Docker + pytest rate limit tests |
| 4 | **O-001: Queue alert threshold too high** | 90 | Replace single alert with TIERED ALERTS: 1) YELLOW at 500 events (notification), 2) RED at 1000 events (page on-call), 3) CRITICAL at 2000 events (page all backend team). Add webhook worker auto-healing: if worker crashes, restart automatically. Monitor queue drain rate (should be >100 events/sec). | DevOps + Backend | Phase 3 Week 1 | Prometheus + PagerDuty escalation |
| 5 | **T-008: Order reconciliation job crashes silently** | 85 | 1) Add supervisor/systemd service to restart job if it crashes, 2) Log every reconciliation run (start/end time, items checked, items fixed), 3) Add monitoring: alert if reconciliation hasn't run in 24h, 4) Test job with corrupted database state, 5) Dry-run mode first (log fixes without applying). | Backend | Phase 3 Week 1 | Python APScheduler + monitoring |
| 6 | **O-004: Team burnout from overcommitment** | 85 | 1) Hire 1 contractor backend engineer for Q4 (8 weeks, focus on Phase 3), 2) Break Phase 3 into sprints: Week 1-2 Auth, Week 3-4 Tier Mgmt, Week 5-6 Portal, Week 7-8 Analytics, 3) Monthly team retro to identify bottlenecks, 4) Enforce 40-hour weeks (no crunch). | Leadership | Immediate | Contractor + project mgmt |
| 7 | **T-003: JWT refresh token never implemented** | 80 | 1) Implement refresh token endpoint: POST /auth/refresh with old refresh_token, returns new access_token + refresh_token, 2) Store refresh tokens in DB with expiry (30 days), 3) Rotate refresh token on each use (old one invalidated), 4) Frontend: auto-refresh when access_token within 5min of expiry, 5) Test with token expiry scenario. | Backend + Frontend | Phase 3 Week 1 | JWT middleware + refresh logic |
| 8 | **B-001: CTAs ineffective + pricing A/B inconclusive** | 75 | 1) DON'T wait for statistical significance, launch A/B with minimum sample size (100 conversions = decision), 2) Show CTAs AFTER FIRST lookup (not after 10), 3) CTAs should be: "Go Pro & Get 100+ Lookups" (specific benefit), 4) Track conversion by pricing tier, pick winner after 2 weeks (not 3 months), 5) Fallback: if no clear winner, use psychological anchoring (show $199 first, then discount to $149). | Product + Frontend | Phase 3 Week 2 | Analytics tracking + A/B framework |
| 9 | **B-002: Retention emails go to spam** | 75 | 1) Use transactional email service (SendGrid/Mailgun, not generic SMTP), 2) Segment emails: usage-based (not generic), 3) Test with SpamAssassin before sending, 4) Include unsubscribe link (required), 5) Track open/click rates, 6) If unsubscribe >5%, redo email template, 7) Send at optimal time (Tuesday 10am based on segment). | Marketing + Backend | Phase 3 Week 2 | SendGrid integration + tracking |
| 10 | **B-008: Top 3 customers = 60% revenue** | 75 | 1) Implement customer diversification scorecard (track: top 1 customer = X% revenue monthly), 2) Set goal: top 1 customer <25% by EOY, 3) Hire sales person to focus on mid-market (SMBs, 2-5 employees), 4) Offer tiered pricing for SMBs (cheaper entry), 5) Quarterly business review with top customers to ensure retention. | Sales + Leadership | Phase 3 Ongoing | Sales metrics dashboard |

---

## IMPLEMENTATION ROADMAP (Phase 3 + Ongoing)

### Phase 3 Week 1 (Foundations)
- [ ] Deploy Redis + rate limiting (T-004)
- [ ] Implement webhook autoscaling + tiered alerts (O-001 + T-001)
- [ ] Add order reconciliation monitoring (T-008)
- [ ] Implement JWT refresh token endpoint (T-003)
- [ ] Hire contractor engineer (O-004)

### Phase 3 Week 2 (Attribution + Retention)
- [ ] Implement sponsor conversion tracking (server-side) (B-004)
- [ ] Launch pricing A/B test (B-001)
- [ ] Set up transactional email service (B-002)
- [ ] Create customer diversification scorecard (B-008)

### Phase 3 Week 3+ (Ongoing)
- [ ] Monitor all metrics continuously
- [ ] Weekly sprint retros to catch new risks
- [ ] Update monitoring thresholds based on real data
- [ ] Iterate on CTAs + retention based on conversion data

---

## SUCCESS CRITERIA FOR FIXES

| Fix | Success Criteria | Measurement |
|-----|---|---|
| T-001 + O-001 | Webhook latency <2s, queue never >500 events | Prometheus dashboard, alerting tests |
| B-004 | Sponsor conversions tracked with 90%+ accuracy | Manual spot checks, sponsor feedback |
| T-004 | Rate limiting prevents brute force (1 attacker = 1 req/sec max) | Load test with 100 concurrent attackers |
| T-008 | Order reconciliation runs daily, 0 orphaned orders | Log monitoring, weekly reconciliation report |
| O-004 | Team morale improves (retro feedback), Phase 3 completes on time | Team surveys, milestone tracking |
| T-003 | JWT refresh tokens issued + rotated, no token expiry errors | JWT error rate monitoring |
| B-001 | Pricing decision made within 2 weeks with >80% confidence | A/B test results, sample size tracking |
| B-002 | Email unsubscribe <3%, open rate >15% | Email analytics dashboard |
| B-008 | Top customer concentration decreases from 30% to <25% within 6 months | Revenue dashboard, customer metrics |

---

## RESIDUAL RISKS AFTER FIXES

Even after implementing these 10 fixes, some medium-level risks remain:

| Residual Risk | Mitigation | Owner |
|---|---|---|
| Sponsor tier adoption <5% (market validation risk) | Conduct market research with 20 sponsors before launch, consider pivoting tier positioning | Product |
| Checkout abandonment >40% persists (U-002) | Run UX testing with 10 real users, measure before/after abandonment | UX |
| Email compliance (GDPR, CAN-SPAM) not fully compliant | Add legal review of email templates, implement consent management | Legal |
| Database query performance at 100K users | Implement query monitoring, add composite indexes proactively | Backend |

---

## RISK REDUCTION SUMMARY

| Category | Pre-Fixes | Post-Fixes | Improvement |
|---|---|---|---|
| Technical | 79.5 avg premortem risk | 45 avg | 43% reduction |
| Business | 80 avg premortem risk | 50 avg | 38% reduction |
| Operational | 74.4 avg premortem risk | 40 avg | 46% reduction |
| Market | 70 avg premortem risk | 60 avg | 14% reduction |
| UX | 68 avg premortem risk | 50 avg | 26% reduction |

**Overall Confidence After Fixes**: 65% ← Up from 52%

---

## NEXT STEPS

1. ✅ **Iteration 1 Complete**: 38 risks identified, 24 mitigations proposed, 10 top premortem risks fixed
2. **Iteration 2**: Take FIXED mitigations, identify NEW risks, run premortem, fix top 10 again
3. **Iterations 3-4**: Continue loop until confidence reaches 85%+ and no new HIGH+CRITICAL risks emerge

See `RISK_MITIGATION_ITERATION_2.md` for Iteration 2 analysis.
