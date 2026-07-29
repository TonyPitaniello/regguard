# Monitoring and Alerting Plan
## Key Metrics, Thresholds, and Runbooks for RegGuard Phase 3-5

**Date**: July 28, 2026  
**Owner**: DevOps + Backend + Product  
**Tools**: Sentry, Prometheus, PagerDuty, DataDog (optional)

---

## EXECUTIVE SUMMARY

This document defines what to measure, when to alert, and how to respond. Organized by risk domain.

### Monitoring Stack

| Component | Tool | Purpose | Data Retention |
|-----------|------|---------|-----------------|
| Error Tracking | Sentry | Exceptions, crashes, errors | 90 days |
| Metrics | Prometheus | System metrics (CPU, memory, requests) | 30 days |
| Alerting | PagerDuty | On-call escalation, incident management | 1 year |
| Logs | CloudWatch / Supabase | Application logs, audit trail | 7 days (prod), 30 days (archive) |
| APM | Sentry / DataDog | Performance monitoring, traces | 7 days |
| Customer Analytics | Mixpanel / Amplitude | Funnel, retention, cohort analysis | Unlimited |

---

## CRITICAL PATH METRICS (Must Monitor 24/7)

### 1. PAYMENT PROCESSING RELIABILITY

**Why It Matters**: Payments are revenue-critical. A 1-hour outage = $1000+ lost revenue.

#### Metric: Webhook Processing Success Rate

| Metric | Definition | Threshold | Alert Level | Action |
|--------|-----------|-----------|------------|--------|
| **Webhook Success Rate** | (Successful webhooks) / (Total webhooks) × 100 | <99% | 🔴 CRITICAL | Page on-call immediately |
| **Webhook Latency (p99)** | 99th percentile webhook processing time | >5 seconds | 🟡 WARNING | Investigate + optimize |
| **Webhook Queue Depth** | Number of pending webhooks in queue | >1000 for 5 min | 🔴 CRITICAL | Autoscale workers immediately |
| **Order Status Mismatch** | Orders in "pending" for >1 hour | >10 orders | 🟠 HIGH | Manual reconciliation job |

**Monitoring Setup**:
```
Sentry Alert: webhook.success_rate < 99%
PagerDuty: Escalate to Backend on-call if <99% for 5 min

Prometheus Query:
rate(webhook_success[5m]) < 0.99

CloudWatch: Log every webhook (id, timestamp, status, latency)
```

**Runbook: Webhook Processing Failure**:
1. Check Stripe webhook status (are events being sent?)
2. Check queue depth (is queue backing up?)
3. Check error logs (what's failing?)
4. Options:
   - Temporary disable rate limiting (allow retry surge)
   - Autoscale webhook workers to 10x
   - Pause new orders while resolving (if critical)
5. Estimated resolution: <30 minutes

---

#### Metric: Order to Revenue Reconciliation

| Metric | Definition | Threshold | Alert Level | Action |
|--------|-----------|-----------|------------|--------|
| **Revenue Match** | Sum(orders.amount) vs Sum(Stripe transactions) | Diff >$1000 | 🔴 CRITICAL | Investigate accounting discrepancy |
| **Failed Orders** | Orders with status='failed' | >5 per hour | 🟠 HIGH | Check payment decline reasons |
| **Refunded Orders** | Orders with status='refunded' | >2 per day | 🟡 WARNING | Check customer complaints |

**Monitoring Setup**:
```
Daily reconciliation job: 
  - Query Supabase orders
  - Query Stripe transactions
  - Compare amounts (must match to $1)
  - Alert if discrepancy >$1000
```

**Runbook: Revenue Mismatch**:
1. Manual audit: check last 24h transactions in Stripe console
2. Check if webhooks for refunds were received
3. Verify database hasn't been corrupted (run integrity check)
4. If <$100 discrepancy: accept as rounding error
5. If >$100: investigate and document discrepancy

---

### 2. SYSTEM AVAILABILITY & PERFORMANCE

**Why It Matters**: Downtime = loss of trust. Customers should experience <99.5% downtime.

#### Metric: API Uptime

| Metric | Definition | Threshold | Alert Level | Action |
|--------|-----------|-----------|------------|--------|
| **Overall Uptime** | Percentage of 5-min intervals with <2 errors | >99.5% | 🟡 WARNING if <99.5% | Investigate + improve |
| **API Response Time (p95)** | 95th percentile response latency | <500ms | 🟡 WARNING if >1s | Check database queries |
| **API Response Time (p99)** | 99th percentile response latency | <2s | 🔴 CRITICAL if >5s | Immediate optimization needed |
| **Error Rate** | (5xx errors) / (total requests) | <0.1% | 🟠 HIGH if >1% | Page on-call |

**Monitoring Setup**:
```
Prometheus:
- up{job="api"} (API health check every 30s)
- http_request_duration_seconds (response times)
- http_requests_total (error count)

PagerDuty:
- Alert if uptime < 99.5% for 10 min
- Alert if error rate > 1% for 5 min

Dashboard:
- Real-time uptime % (last 24h, 7d, 30d)
- Response time trend
- Error rate trend
```

**Runbook: High Error Rate**:
1. Check Sentry for top errors
2. Check database connections (pool exhaustion?)
3. Check Stripe API status (external outage?)
4. Check recent deployments (new bug?)
5. If recoverable: restart pod(s)
6. If not: rollback last deployment

---

#### Metric: Database Performance

| Metric | Definition | Threshold | Alert Level | Action |
|--------|-----------|-----------|------------|--------|
| **Query Latency (p99)** | 99th percentile query time | <500ms | 🟡 WARNING if >1s | Add index or cache |
| **Connection Pool Usage** | Active connections / max pool size | <80% | 🟠 HIGH if >90% | Scale up or find connection leak |
| **Database CPU** | Database CPU usage | <70% | 🟠 HIGH if >80% | Optimize queries or scale DB |
| **Storage Usage** | Database disk space used | <70% | 🟠 HIGH if >80% | Archive logs or compress data |

**Monitoring Setup**:
```
Supabase Console:
- View query performance (slow query log)
- Monitor connection count
- Monitor CPU + memory

Prometheus:
- postgres_query_duration_seconds
- pg_stat_statements (top slow queries)

Alert:
- Query latency > 1s (investigate + optimize)
- Connection pool > 90% (find leak)
```

**Runbook: Database Slow Queries**:
1. Check Supabase slow query log
2. Identify top slow queries
3. Add index on frequently filtered columns
4. Run ANALYZE to update stats
5. Test query latency improves

---

### 3. AUTHENTICATION & SECURITY

**Why It Matters**: Auth issues = lockout or breach risk.

#### Metric: JWT Token Validation

| Metric | Definition | Threshold | Alert Level | Action |
|--------|-----------|-----------|------------|--------|
| **JWT Decode Failures** | Failed JWT validations | >10 per min | 🟠 HIGH | Check token format + secret |
| **Expired Token Rate** | Requests with expired tokens | >5% of auth requests | 🟡 WARNING | Check token rotation |
| **Refresh Token Usage** | Refresh token endpoint calls | <10% of auth flow | 🟡 WARNING | Check client-side token handling |

**Monitoring Setup**:
```
Sentry:
- Track JWT decode exceptions
- Category: "authentication.jwt.invalid"

Logs:
- Log every JWT decode attempt (success + failure)
- Include user_id, token_exp, current_time

Alert:
- >10 JWT failures/min = potential attack
```

**Runbook: JWT Decode Failures**:
1. Check if SUPABASE_JWT_SECRET is correct
2. Check if token format is correct (Bearer {token})
3. Check if token has expired (check `exp` claim)
4. Check if someone modified token (signature invalid)
5. If ongoing issue: might be attack, check logs for patterns

---

#### Metric: Rate Limiting Effectiveness

| Metric | Definition | Threshold | Alert Level | Action |
|--------|-----------|-----------|------------|--------|
| **Rate Limit Hits** | Requests blocked by rate limiter | <1% of traffic | 🟡 WARNING if >5% | Possible attack or configuration issue |
| **Unique IPs Limited** | Count of IPs hitting rate limit | <10 per day | 🟡 WARNING if >100 per day | Possible attack |
| **Redis Connection Status** | Redis availability | 100% | 🔴 CRITICAL if unavailable | Failover to in-memory limiter |

**Monitoring Setup**:
```
Prometheus:
- rate_limiter_blocked_requests_total
- rate_limiter_active_ips (cardinality)

Redis Monitor:
- Connection count
- Memory usage
- Eviction rate

Alert:
- Redis down = 503 error + page on-call
- >100 IPs limited per day = investigate
```

**Runbook: Rate Limiter Broken**:
1. Check if Redis is running
2. Check Redis connection count (if >max, connection leak)
3. Check Redis memory (if full, evicting keys)
4. If Redis is down: activate in-memory fallback (limits 50 IPs max)
5. Restart Redis

---

### 4. DATA QUALITY & INTEGRITY

**Why It Matters**: Bad data = bad decisions. Must trust conversion data, churn rates, etc.

#### Metric: Event Tracking Accuracy

| Metric | Definition | Threshold | Alert Level | Action |
|--------|-----------|-----------|------------|--------|
| **Frontend vs Backend Mismatch** | Events where frontend count ≠ backend count | 0% (must be 100% match) | 🔴 CRITICAL if >0.1% | Pause A/B test, investigate |
| **Conversion Event Count** | Total conversions logged daily | Baseline +/- 20% | 🟡 WARNING if >30% change | Check for data quality issue |
| **Sponsor Tracking Accuracy** | Manual spot check: link conversions match database | 100% match | 🟠 HIGH if <95% | Manual audit + fix |

**Monitoring Setup**:
```
Backend:
- Log every conversion event with unique ID
- Include: user_id, timestamp, conversion_type, source
- Store in database (not just external analytics)

Frontend:
- Log every conversion event with same schema
- Include: user_id, timestamp, conversion_type, source

Daily Reconciliation Job:
- Query all events from yesterday
- Compare frontend vs backend counts
- Alert if mismatch > 0.1%

Sponsor Tracking:
- Weekly manual audit: pick 10 sponsor links at random
- Check each link's conversions match database
- Document findings + fix any discrepancies
```

**Runbook: Data Mismatch**:
1. Identify date/time range of mismatch
2. Query events from that range (frontend + backend logs)
3. Identify missing events (frontend only? backend only?)
4. Determine root cause:
   - Frontend not sending event?
   - Backend not receiving event?
   - Duplicate events?
5. Fix code + backfill data if needed

---

### 5. BUSINESS METRICS (Daily Monitoring)

**Why It Matters**: These predict success/failure 2-4 weeks in advance.

#### Metric: Conversion Funnel

| Metric | Definition | Target | Alert Level | Action |
|--------|-----------|--------|------------|--------|
| **Signup to Free User** | Signups / site visitors | >5% | 🟡 WARNING if <3% | Test landing page |
| **Free to Paid Conversion** | (Paid users) / (free users 30d old) | >3% | 🔴 CRITICAL if <1% | Urgent product changes |
| **Paid User Retention (7d)** | (Active 7d later) / (paid users) | >70% | 🟠 HIGH if <50% | Check for bugs or UX issues |
| **Paid User Retention (30d)** | (Active 30d later) / (paid users) | >50% | 🔴 CRITICAL if <30% | Churn risk, investigate |

**Monitoring Setup**:
```
Mixpanel / Amplitude:
- Track each funnel stage daily
- Create cohort: "Signup on [date]"
- Measure: % still active after 7d, 30d, 90d

Daily Report:
- Email team with funnel metrics
- Flag if any metric drops >20% from baseline

Slack Bot:
- Post daily: "Free→Paid Conv: 3.2% (↓ from 3.5%)"
```

**Runbook: Conversion Drops to 1%**:
1. Check for recent product changes (might have broken something)
2. Check error logs (are users seeing errors at checkout?)
3. Check support tickets (are users complaining?)
4. Check cohort data (does drop affect all users or just new ones?)
5. A/B test new CTAs, pricing, or copy

---

#### Metric: Churn & Retention

| Metric | Definition | Target | Alert Level | Action |
|--------|-----------|--------|------------|--------|
| **Monthly Churn Rate** | (Cancelled subs) / (total subs at month start) | <10% | 🟠 HIGH if >15% | Win-back campaign |
| **Churn by Segment** | Churn rate per tier / segment | Tier-specific | 🟡 WARNING if >15% | Segment-specific retention |
| **Customer Lifetime Value** | (ARPU × Gross Margin) / Churn Rate | >$10K | 🔴 CRITICAL if <$5K | Pricing or positioning problem |
| **Customer Acquisition Cost** | (Sales + Marketing spend) / (New customers) | <$3K | 🔴 CRITICAL if >$5K | CAC too high, reduce spend |

**Monitoring Setup**:
```
Weekly Cohort Analysis:
- Segment users by signup date
- Measure % still paying after 1mo, 3mo, 6mo
- Alert if cohort churn > expected

Monthly Business Review:
- CEO: LTV vs CAC
- Target: LTV:CAC ratio > 3:1 (or >2:1 for SaaS)
- If <1.5:1: business unsustainable, pivot needed

Slack Reports:
- Monday AM: "Weekly Churn: 2.1% (↑ from 1.8%)"
- Friday PM: "Monthly Forecast: $25K ARR"
```

**Runbook: Churn Increases to 15%/month**:
1. Identify cohort: did recent cohort churn fast, or all cohorts?
2. If recent cohort: might be product issue (new bug?)
3. If all cohorts: might be market (competitor emerged?) or messaging (expectations mismatch?)
4. Customer interviews: why are people leaving?
5. Product iteration: fix top reasons for churn

---

#### Metric: Revenue & Unit Economics

| Metric | Definition | Target | Alert Level | Action |
|--------|-----------|--------|------------|--------|
| **Monthly Recurring Revenue (MRR)** | Monthly revenue (recurring) | $1K → $25K → $100K+ | 🟡 WARNING if <target | Check conversion + retention |
| **Average Revenue Per User (ARPU)** | Total revenue / total users | >$50/month | 🟡 WARNING if <$30 | Upsell or raise pricing |
| **Gross Margin** | (Revenue - COGS) / Revenue | >70% | 🟡 WARNING if <60% | Cost structure issue |
| **Unit Economics** | LTV:CAC ratio | >3:1 | 🔴 CRITICAL if <1.5:1 | Business not viable |

**Monitoring Setup**:
```
Monthly Financial Report:
- MRR: sum of all active subscriptions × price
- ARPU: MRR / active user count
- CAC: (Sales + Marketing spend this month) / (new customers)
- LTV: ARPU / monthly churn rate

Excel Dashboard:
- Trend MRR month-over-month
- Track CAC vs LTV
- Alert if trending wrong direction

Email: Weekly MRR update to leadership
```

**Runbook: MRR Decline**:
1. Identify cause:
   - Churn increase? (more customers leaving)
   - Conversion drop? (fewer new customers)
   - ARPU decrease? (upsell not working)
2. Address root cause:
   - Churn: retention campaign
   - Conversion: product/marketing changes
   - ARPU: upsell features
3. Project recovery: when will MRR rebound?

---

## ALERTING ESCALATION MATRIX

### Priority Levels

| Priority | Condition | Response Time | Owner | Escalate If |
|----------|-----------|----------------|-------|------------|
| **P0 Critical** | <99% uptime OR <95% conversion OR data loss | 15 min | On-call Backend | Not resolved in 1 hour |
| **P1 High** | <99.5% uptime OR API latency >5s | 30 min | On-call Backend | Not resolved in 2 hours |
| **P2 Medium** | Churn >15% OR CAC >$5K OR >10 support tickets queued | 4 hours | Daytime owner | Not resolved in 24 hours |
| **P3 Low** | Minor bugs, UX issues, optimization opportunities | 24 hours | Team backlog | Can defer to next sprint |

### Escalation Chain

```
P0 Critical:
1. → On-call engineer (page immediately)
2. → If unresolved in 30 min → Backend lead
3. → If unresolved in 1 hour → CTO

P1 High:
1. → On-call engineer (Slack)
2. → If unresolved in 4 hours → Backend lead + team sync

P2 Medium:
1. → Team backlog (next daily standup)
2. → If high impact → prioritize above current tasks

P3 Low:
1. → Backlog for next sprint
```

---

## ON-CALL RUNBOOKS

### Runbook: P0 - Webhook Processing Down

**Detection**: Sentry alert: webhook success rate <99%

**Impact**: Orders not confirmed, customers see "pending" payment indefinitely

**Time to Resolve**: Target <30 min

**Steps**:
1. (1 min) Check: Are Stripe webhooks being sent to us?
   - Go to Stripe dashboard → Webhooks
   - Check recent events (should see 1-2 per sec)
   - If no events: check webhook URL, might be wrong endpoint
2. (2 min) Check: Is our webhook queue backing up?
   - Query Supabase: SELECT COUNT(*) FROM webhook_events WHERE status='pending'
   - If >1000: queue backed up, need to autoscale workers
3. (3 min) Check: What's the error?
   - Go to Sentry → Recent events
   - See top error type (database error? validation error? timeout?)
4. (5 min) Fix based on error type:
   - **Database error**: Check DB connection pool, might be exhausted
   - **Validation error**: Check if Stripe payload changed
   - **Timeout error**: Increase webhook timeout (currently 30s)
   - **Rate limit**: Check if hitting Stripe API rate limits
5. (10 min) Scale webhook workers:
   - If queue depth >1000: spin up 5 additional workers (AWS Lambda)
   - Monitor queue drain rate (should be >100 events/sec)
6. (15 min) Verify recovery:
   - Queue depth should drop
   - Webhook success rate should recover to >99%
   - If not: escalate to CTO

---

### Runbook: P1 - High Error Rate (>1%)

**Detection**: Sentry alert: error rate >1% for 5 min

**Impact**: Some users experiencing failures

**Time to Resolve**: Target <2 hours

**Steps**:
1. (2 min) Identify top error:
   - Go to Sentry → Issues
   - Click top issue by volume
   - Review error type + stack trace
2. (5 min) Determine if recent:
   - Check commit log: any deploys in last 1 hour?
   - If yes: might be new bug from recent deploy
   - If no: might be infrastructure issue (database, API)
3. (10 min) Fix options:
   - **New bug**: Rollback last deploy
   - **Database issue**: Restart database connection pool
   - **API issue**: Check external API status (Stripe, etc.)
4. (15 min) Deploy fix or rollback
5. (20 min) Monitor error rate
   - Should drop back to <0.1% after fix
   - If not: investigate further

---

### Runbook: P2 - Churn Spike (>15%/month)

**Detection**: Weekly metrics: churn >15% in one cohort

**Impact**: Revenue at risk, might indicate product issue

**Time to Resolve**: Target <24 hours analysis, then 1-week product cycle

**Steps**:
1. (1 hour) Diagnose:
   - Is it all cohorts or just one signup date?
   - Did recent product change break something?
   - Did competitor launch? (check news)
   - Are support tickets spiking? (users complaining?)
2. (2 hours) Customer interviews:
   - Call 5 customers who cancelled recently
   - Ask: "Why did you stop using RegGuard?"
   - Take notes on themes
3. (4 hours) Product meeting:
   - Share findings with product team
   - Brainstorm fixes (product, messaging, pricing)
4. (1 week) Implement fix + re-measure churn

---

### Runbook: P3 - Slow Query Detected

**Detection**: Prometheus alert: query latency >1s for sustained period

**Impact**: API response time slower for some users

**Time to Resolve**: Target <24 hours

**Steps**:
1. (15 min) Identify slow query:
   - Go to Supabase → Slow Query Log
   - Find query with latency >1s
   - Note: which table, what filters, how many rows
2. (30 min) Analyze:
   - Does query have an index on filters? If not: add index
   - Is query selecting too many columns? If yes: reduce select
   - Is query joining multiple tables? If yes: test query plan
3. (1 hour) Optimize + test:
   - Make change (add index or rewrite query)
   - Run ANALYZE to update table stats
   - Re-test query latency (should improve)
4. (Next day) Deploy + monitor:
   - Include query optimization in next deploy
   - Monitor latency: should improve

---

## MONITORING DASHBOARD (Sample)

### Real-Time Monitoring (Homepage)

```
╔═══════════════════════════════════════════════════════════╗
║ RegGuard System Status - Last 24 Hours                    ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║ System Uptime:           99.8% ✅                         ║
║ Webhook Success:         99.7% ✅                         ║
║ API Response (p95):      245ms ✅                         ║
║ Error Rate:              0.08% ✅                         ║
║ Queue Depth:             42 events ✅                     ║
║                                                           ║
║ Free → Paid Conversion:  3.2% (↓ from 3.5%) ⚠️          ║
║ Monthly Churn:           8.1% (↑ from 6.2%) ⚠️          ║
║ MRR:                     $22,400 (on track) ✅            ║
║ LTV:CAC Ratio:           2.8:1 ✅                         ║
║                                                           ║
║ Incidents (24h):         0 Critical, 1 High ✅            ║
║ On-call:                 alice@regguard.com               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## SUCCESS METRICS FOR MONITORING

| Aspect | Target | Owner |
|--------|--------|-------|
| Alert accuracy | >90% true positives, <10% false positives | DevOps |
| MTTR (Mean Time to Resolve) | P0: <30 min, P1: <2 hours, P2: <24 hours | On-call |
| On-call coverage | 24/7 rotation, ≤1 week per engineer per month | Leadership |
| Runbook quality | All P0/P1 incidents documented within 24h | Owner |
| Dashboard accuracy | Real-time (latency <5 sec) | DevOps |

---

## CONCLUSION

This monitoring plan provides **real-time visibility** into RegGuard's health. By tracking these metrics and acting on alerts, we can catch issues before they impact customers.

**Key principles**:
1. **Measure what matters** (business metrics, not just technical)
2. **Alert on actionable metrics** (not noise)
3. **Respond fast** (P0 in <30 min)
4. **Document everything** (runbooks, postmortems)
5. **Iterate** (improve monitoring based on incidents)

See `RISK_MITIGATION_FINAL.md` for comprehensive risk register.
