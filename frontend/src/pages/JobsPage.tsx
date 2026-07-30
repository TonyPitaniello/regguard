/**
 * Saved Jobs — reopen past site diligence, open /r/{id}, re-run research.
 */

import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Briefcase,
  ExternalLink,
  Loader2,
  MapPin,
  RefreshCw,
  Trash2,
  AlertCircle,
  Plus,
} from 'lucide-react';
import { backendUrl } from '../env';
import {
  getJobsEmail,
  getOwnerKey,
  setJobsEmail,
  type SavedJob,
} from '../jobsOwner';

export default function JobsPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState(getJobsEmail());
  const [jobs, setJobs] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');

  const loadJobs = useCallback(async (emailValue: string) => {
    const ownerKey = getOwnerKey();
    if (!emailValue && !ownerKey) {
      setJobs([]);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (emailValue) params.set('email', emailValue);
      if (ownerKey) params.set('owner_key', ownerKey);
      const res = await fetch(backendUrl(`/jobs?${params.toString()}`));
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed to load jobs (${res.status})`);
      }
      const data = await res.json();
      setJobs(data.jobs || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const existing = getJobsEmail();
    if (existing) {
      setEmail(existing);
      void loadJobs(existing);
    }
  }, [loadJobs]);

  const handleLookup = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = email.trim();
    if (!trimmed || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      setError('Enter the email you used on free trial');
      return;
    }
    setJobsEmail(trimmed);
    void loadJobs(trimmed);
  };

  const showToast = (msg: string) => {
    setToast(msg);
    window.setTimeout(() => setToast(''), 2800);
  };

  const handleDelete = async (job: SavedJob) => {
    if (!window.confirm(`Remove saved job for ${job.address}?`)) return;
    const params = new URLSearchParams();
    if (email) params.set('email', email);
    params.set('owner_key', getOwnerKey());
    const res = await fetch(backendUrl(`/jobs/${job.id}?${params.toString()}`), {
      method: 'DELETE',
    });
    if (res.ok) {
      setJobs((prev) => prev.filter((j) => j.id !== job.id));
      showToast('Job removed');
    } else {
      setError('Could not delete job');
    }
  };

  const handleRerun = (job: SavedJob) => {
    sessionStorage.setItem(
      'regguard_job_prefill',
      JSON.stringify({
        address: job.address,
        city: job.city || '',
        state: job.state || '',
        zip: job.zip || '',
        projectType: job.project_type || 'general',
        email: job.owner_email || email,
        jobId: job.id,
      })
    );
    navigate('/free-trial');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-3xl mx-auto px-4 py-10 sm:px-6 space-y-8">
        <header className="space-y-3 border-b border-slate-800 pb-6">
          <p className="text-xs font-bold uppercase tracking-wide text-purple-300 flex items-center gap-2">
            <Briefcase className="w-3.5 h-3.5" />
            Saved Jobs
          </p>
          <h1 className="text-3xl font-black">Your site diligence workspace</h1>
          <p className="text-gray-300 text-sm leading-relaxed">
            Reopen past lookups, open the shareable bid-file report, or re-run research for the same
            address. Jobs are saved automatically when you run a free trial.
          </p>
        </header>

        <form onSubmit={handleLookup} className="flex flex-col sm:flex-row gap-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email used on free trial"
            className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2.5 text-sm text-white placeholder:text-gray-500"
          />
          <button
            type="submit"
            className="rounded-lg bg-purple-600 hover:bg-purple-500 px-4 py-2.5 text-sm font-semibold"
          >
            Load jobs
          </button>
        </form>

        {toast && (
          <p className="text-sm text-emerald-300" role="status">
            {toast}
          </p>
        )}
        {error && (
          <div className="flex gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            {error}
          </div>
        )}

        <div className="flex justify-between items-center">
          <p className="text-sm text-gray-400">
            {loading ? 'Loading…' : `${jobs.length} job${jobs.length === 1 ? '' : 's'}`}
          </p>
          <Link
            to="/free-trial"
            className="inline-flex items-center gap-2 text-sm font-semibold text-purple-300 hover:text-purple-200"
          >
            <Plus className="w-4 h-4" />
            New lookup
          </Link>
        </div>

        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm py-8 justify-center">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading jobs…
          </div>
        )}

        {!loading && jobs.length === 0 && email && (
          <div className="rounded-lg border border-slate-800 bg-slate-900/50 px-4 py-8 text-center text-sm text-gray-400">
            No saved jobs for this email yet. Run a free trial — it will appear here automatically.
          </div>
        )}

        <ul className="space-y-3">
          {jobs.map((job) => {
            const snap = job.summary_snapshot || {};
            const reportUrl =
              job.share_url ||
              (job.last_research_id ? `https://app.regguardagent.com/r/${job.last_research_id}` : '');
            return (
              <li
                key={job.id}
                className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 space-y-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-bold text-white flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-purple-300 shrink-0" />
                      {job.address}
                    </p>
                    <p className="text-sm text-gray-400 mt-1">
                      {[job.city, job.state, job.zip].filter(Boolean).join(', ')}
                      {job.project_type ? ` · ${job.project_type}` : ''}
                    </p>
                  </div>
                  {snap.preview && (
                    <span className="text-[10px] font-bold uppercase tracking-wide text-amber-300 border border-amber-500/40 rounded px-1.5 py-0.5">
                      Preview
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-3 text-xs text-gray-400">
                  {snap.estimated_timeline && <span>Timeline: {snap.estimated_timeline}</span>}
                  {snap.estimated_total_cost != null && (
                    <span>Est. ${Number(snap.estimated_total_cost).toLocaleString()}</span>
                  )}
                  {snap.punch_count != null && <span>{snap.punch_count} punch items</span>}
                  {job.last_run_at && (
                    <span>Last run: {new Date(job.last_run_at).toLocaleDateString()}</span>
                  )}
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                  {reportUrl && (
                    <a
                      href={reportUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs font-semibold text-amber-100 hover:bg-amber-500/20"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      Open report
                    </a>
                  )}
                  <button
                    type="button"
                    onClick={() => handleRerun(job)}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-purple-500/40 bg-purple-500/10 px-3 py-2 text-xs font-semibold text-purple-100 hover:bg-purple-500/20"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    Re-run research
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleDelete(job)}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-600 px-3 py-2 text-xs font-semibold text-gray-300 hover:bg-slate-800"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Remove
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
