/**
 * Local identity for Saved Jobs (email + device owner_key).
 * Matches the Orders page pattern (email in sessionStorage).
 */

const OWNER_KEY = 'regguard_owner_key';
const EMAIL_KEY = 'userEmail';

export function getOwnerKey(): string {
  if (typeof window === 'undefined') return '';
  let key = localStorage.getItem(OWNER_KEY);
  if (!key) {
    key =
      typeof crypto !== 'undefined' && crypto.randomUUID
        ? `own-${crypto.randomUUID()}`
        : `own-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(OWNER_KEY, key);
  }
  return key;
}

export function getJobsEmail(): string {
  if (typeof window === 'undefined') return '';
  return (sessionStorage.getItem(EMAIL_KEY) || localStorage.getItem('regguard_jobs_email') || '').trim();
}

export function setJobsEmail(email: string) {
  if (typeof window === 'undefined' || !email) return;
  sessionStorage.setItem(EMAIL_KEY, email);
  localStorage.setItem('regguard_jobs_email', email);
}

export type SavedJob = {
  id: string;
  owner_email: string;
  owner_key?: string;
  address: string;
  city?: string;
  state?: string;
  zip?: string;
  project_type?: string;
  status?: string;
  last_research_id?: string;
  share_url?: string;
  last_run_at?: string;
  summary_snapshot?: {
    estimated_timeline?: string;
    estimated_total_cost?: number;
    risk_level?: string;
    preview?: boolean;
    punch_count?: number;
  };
  notes?: string;
  created_at?: string;
  updated_at?: string;
};
