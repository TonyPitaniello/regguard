-- Forwardable research reports (shareable /r/{id})
-- Run in Supabase SQL editor. Local filesystem store works without this table.

CREATE TABLE IF NOT EXISTS research_reports (
  id TEXT PRIMARY KEY,
  analysis JSONB NOT NULL,
  project_address TEXT,
  project_city TEXT,
  project_state TEXT,
  project_zip TEXT,
  preview BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_research_reports_created_at ON research_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_reports_zip ON research_reports(project_zip);
CREATE INDEX IF NOT EXISTS idx_research_reports_expires_at ON research_reports(expires_at);

ALTER TABLE research_reports ENABLE ROW LEVEL SECURITY;

-- Public read of non-expired reports (share links). Writes via service role only.
DROP POLICY IF EXISTS "Public can read research reports" ON research_reports;
CREATE POLICY "Public can read research reports" ON research_reports
  FOR SELECT USING (expires_at IS NULL OR expires_at > now());

DROP POLICY IF EXISTS "Service role manages research reports" ON research_reports;
CREATE POLICY "Service role manages research reports" ON research_reports
  FOR ALL USING (true) WITH CHECK (true);

GRANT SELECT ON research_reports TO anon, authenticated;
GRANT ALL ON research_reports TO service_role;
