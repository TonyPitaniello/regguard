# Forwardable artifact

Makes free-trial / research results something a GC can put in a bid file.

## What shipped

1. **Persist research** — `backend/research_store.py`
   - Local JSON under `backend/data/research_reports/` (always on)
   - Optional Supabase table `research_reports` (`migrations/011_research_reports.sql`)
   - PII (email/phone) stripped from public payloads
   - Default TTL 90 days (`REG_GUARD_REPORT_TTL_DAYS`)

2. **APIs**
   - `POST /research/persist` — save analysis → `{ research_id, share_url }`
   - `GET /research/{id}/report` — public JSON for the share page
   - `GET /r/{id}` — API alias
   - Free-trial response includes `share_url`
   - `_get_research_data` reads the store (no longer a TODO stub)

3. **Full punch + sources email** — `backend/report_email.py`
   - SendGrid/Resend result emails include honesty banner, full punch list, sources, share CTA

4. **Shareable UI** — `/r/:id` → `SharedReportPage.tsx`
   - Modal: **Open bid-file report** + **Copy /r/ link**
   - SMS includes the share URL
   - Mailto fallback includes punch highlights + link

## Env

| Var | Default | Purpose |
|-----|---------|---------|
| `REG_GUARD_APP_URL` | `https://app.regguardagent.com` | Share link host |
| `REG_GUARD_REPORT_DIR` | `backend/data/research_reports` | Local store path |
| `REG_GUARD_REPORT_TTL_DAYS` | `90` | Expiry |
| `SUPABASE_URL` / `SUPABASE_KEY` | — | Durable store (run migration 011) |

## Tests

```bash
cd backend && python -m pytest tests/test_forwardable_artifact.py -q
```
