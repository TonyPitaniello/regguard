# Saved Jobs

Weekly habit loop: reopen past site diligence, open `/r/{id}`, re-run research.

## What shipped

1. **Store** — `backend/jobs_store.py`
   - Local JSON + optional Supabase `saved_jobs`
   - Identity: `owner_email` (primary) + `owner_key` (device id)
   - Dedupes by email + address + zip on upsert

2. **APIs**
   - `POST /jobs` — create/upsert
   - `GET /jobs?email=&owner_key=`
   - `GET /jobs/{id}`
   - `DELETE /jobs/{id}`
   - `POST /jobs/{id}/attach-research`
   - Free-trial auto-saves a job when email + address present

3. **UI**
   - `/jobs` (and `/my-jobs`) — `JobsPage.tsx`
   - Header + sidebar **My Jobs**
   - Results modal: “Saved to My Jobs →”
   - Re-run prefills free-trial form via `regguard_job_prefill`

## Ops

Run `backend/migrations/012_saved_jobs.sql` in Supabase for durable storage.

## Tests

```bash
cd backend && python -m pytest tests/test_saved_jobs.py -q
```
