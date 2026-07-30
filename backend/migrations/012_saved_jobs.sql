-- Saved Jobs (weekly habit loop)
-- Run in Supabase SQL editor. Local filesystem store works without this table.

CREATE TABLE IF NOT EXISTS saved_jobs (
  id TEXT PRIMARY KEY,
  owner_email TEXT NOT NULL,
  owner_key TEXT,
  address TEXT NOT NULL,
  city TEXT,
  state TEXT,
  zip TEXT,
  project_type TEXT DEFAULT 'general',
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived')),
  last_research_id TEXT,
  share_url TEXT,
  last_run_at TIMESTAMPTZ,
  summary_snapshot JSONB DEFAULT '{}'::jsonb,
  notes TEXT DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_saved_jobs_owner_email ON saved_jobs(owner_email);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_updated_at ON saved_jobs(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_status ON saved_jobs(status);

ALTER TABLE saved_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Service role manages saved jobs" ON saved_jobs;
CREATE POLICY "Service role manages saved jobs" ON saved_jobs
  FOR ALL USING (true) WITH CHECK (true);

GRANT ALL ON saved_jobs TO service_role;
