/**
 * ResultsViewerModal — large overlay showing free-trial analysis + text/email send.
 * Stays on the current page (homepage / free-trial); does not require /results navigation.
 */

import { useEffect, useState } from 'react';
import { X, ChevronDown, ChevronUp, Copy, Check, Share2 } from 'lucide-react';
import SendResultsForm, { ResultsSummaryPayload } from './SendResultsForm';
import { areEstimatesUnverified, isRiskScoreHidden, type HonestyMeta } from './honesty';

const APP_URL = 'https://app.regguardagent.com/';

export interface AnalysisData {
  timestamp: string;
  research_id?: string;
  share_url?: string;
  preview?: boolean;
  honesty?: HonestyMeta;
  project_info: {
    address: string;
    city: string;
    state: string;
    zip: string;
    type: string;
    coordinates?: { latitude: number; longitude: number };
  };
  environmental_screening: {
    risk_level: string;
    risk_score_hidden?: boolean;
    findings: Array<{
      category: string;
      risk_level: string;
      description: string;
      action_items: string[];
      data_sources: string[];
      research_cost_usd: number;
    }>;
    total_research_cost: number;
    action_plan: string[];
  };
  punch_list: {
    punch_list: Array<{
      priority: string;
      task: string;
      responsible_party: string;
      timeline: string;
      estimated_cost?: number;
      cost_verified?: boolean;
      notes: string;
    }>;
    timeline_summary: string;
    estimated_total_cost: number;
    estimates_unverified?: boolean;
    critical_path: string[];
    inspection_sequence?: string[];
    ahj_fee_lines?: string[];
    milestones: Array<{ week: string; milestone: string }>;
    who_to_call: Record<string, string>;
  };
  summary: {
    total_environmental_risks: number;
    high_risk_count: number;
    total_punch_list_items: number;
    estimated_timeline: string;
    estimated_total_cost: number;
    estimates_unverified?: boolean;
    cost_verified?: boolean;
    timeline_verified?: boolean;
    risk_verified?: boolean;
    ahj_id?: string;
    inspection_sequence?: string[];
  };
  next_steps: string[];
}

interface ResultsViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  analysis: AnalysisData;
  researchId?: string | null;
  defaultEmail?: string;
  defaultPhone?: string;
}

function buildShareText(analysis: AnalysisData): string {
  const p = analysis.project_info;
  const hideRisk = isRiskScoreHidden(analysis);
  const unverified = areEstimatesUnverified(analysis);
  const risk = hideRisk
    ? 'Risk score unavailable (preview — not for bidding)'
    : `Risk: ${analysis.environmental_screening?.risk_level || 'N/A'}`;
  const timeline = analysis.summary?.estimated_timeline || 'TBD';
  const cost = analysis.summary?.estimated_total_cost;
  const reportUrl =
    analysis.share_url ||
    (analysis.research_id ? `${APP_URL}r/${analysis.research_id}` : APP_URL);
  return [
    `RegGuard site diligence: ${p.address}, ${p.city}, ${p.state} ${p.zip}`,
    risk,
    `Timeline: ${timeline}${unverified && !String(timeline).toLowerCase().includes('unverified') ? ' (unverified)' : ''}`,
    cost != null
      ? `Est. cost: $${Number(cost).toLocaleString()}${unverified ? ' (unverified — not an AHJ quote)' : ''}`
      : '',
    `Full report: ${reportUrl}`,
  ]
    .filter(Boolean)
    .join('\n');
}

function getRiskColor(level: string) {
  switch (level.toUpperCase()) {
    case 'CRITICAL':
      return 'text-red-500 bg-red-50';
    case 'HIGH':
      return 'text-orange-500 bg-orange-50';
    case 'MEDIUM':
      return 'text-yellow-500 bg-yellow-50';
    case 'LOW':
      return 'text-green-500 bg-green-50';
    default:
      return 'text-gray-500 bg-gray-50';
  }
}

function getPriorityBadge(priority: string) {
  switch (priority.toUpperCase()) {
    case 'CRITICAL':
      return 'bg-red-100 text-red-800 border border-red-300';
    case 'HIGH':
      return 'bg-orange-100 text-orange-800 border border-orange-300';
    case 'MEDIUM':
      return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
    case 'LOW':
      return 'bg-blue-100 text-blue-800 border border-blue-300';
    default:
      return 'bg-gray-100 text-gray-800 border border-gray-300';
  }
}

export function buildSummaryFromAnalysis(analysis: AnalysisData): ResultsSummaryPayload {
  const hideRisk = isRiskScoreHidden(analysis);
  const unverified = areEstimatesUnverified(analysis);
  return {
    zip: analysis.project_info?.zip,
    city: analysis.project_info?.city,
    state: analysis.project_info?.state,
    address: analysis.project_info?.address,
    risk_level: hideRisk ? undefined : analysis.environmental_screening?.risk_level,
    risk_unavailable: hideRisk,
    timeline: analysis.summary?.estimated_timeline,
    cost: analysis.summary?.estimated_total_cost,
    estimates_unverified: unverified,
    preview: Boolean(analysis.preview),
  };
}

export default function ResultsViewerModal({
  isOpen,
  onClose,
  analysis,
  researchId,
  defaultEmail = '',
  defaultPhone = '',
}: ResultsViewerModalProps) {
  const [expanded, setExpanded] = useState({
    environmental: true,
    punchList: true,
    critical: true,
  });
  const [copied, setCopied] = useState<'link' | 'text' | 'facebook' | 'instagram' | null>(null);
  const [toast, setToast] = useState('');

  // Lock body scroll while modal is open so the form/map behind cannot float with page scroll
  useEffect(() => {
    if (!isOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prev;
    };
  }, [isOpen]);

  if (!isOpen || !analysis) return null;

  const summary = buildSummaryFromAnalysis(analysis);
  const effectiveResearchId = researchId || analysis.research_id || null;
  const shareText = buildShareText(analysis);
  const hideRisk = isRiskScoreHidden(analysis);
  const unverifiedEstimates = areEstimatesUnverified(analysis);
  const honestyLabels = analysis.honesty?.labels;

  const toggle = (key: keyof typeof expanded) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const showToast = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(''), 3200);
  };

  const copyShareText = async (kind: 'text' | 'facebook' | 'instagram' = 'text') => {
    try {
      await navigator.clipboard.writeText(shareText);
      setCopied(kind);
      window.setTimeout(() => setCopied(null), 2000);
      if (kind === 'instagram') {
        showToast('Caption copied — paste in Instagram DM or Story');
      } else if (kind === 'facebook') {
        showToast('Summary copied — paste into your Facebook post');
      }
      return true;
    } catch {
      showToast('Could not copy — select share text manually');
      return false;
    }
  };

  const openWhatsApp = () => {
    window.open(`https://wa.me/?text=${encodeURIComponent(shareText)}`, '_blank', 'noopener,noreferrer');
  };

  const openFacebook = async () => {
    await copyShareText('facebook');
    window.open(
      `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(APP_URL)}`,
      '_blank',
      'noopener,noreferrer'
    );
  };

  const openInstagram = async () => {
    await copyShareText('instagram');
    window.open('https://www.instagram.com/', '_blank', 'noopener,noreferrer');
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-2 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="results-modal-title"
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-5xl max-h-[92vh] flex flex-col bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-purple-500/30 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 px-5 sm:px-8 py-5 border-b border-slate-700/80 bg-slate-900/90 shrink-0 z-10">
          <div>
            <h2 id="results-modal-title" className="text-2xl sm:text-3xl font-black text-white">
              Your Site Diligence Analysis
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              {analysis.project_info.address} • {analysis.project_info.city},{' '}
              {analysis.project_info.state} {analysis.project_info.zip}
            </p>
            {(analysis.preview || hideRisk || unverifiedEstimates) && (
              <p className="mt-2 inline-flex items-center rounded-md border border-amber-500/40 bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-200">
                Preview — unverified estimates · not AHJ quotes
              </p>
            )}
            <a
              href="/jobs"
              className="mt-2 inline-flex text-xs font-semibold text-purple-300 hover:text-purple-200"
            >
              Saved to My Jobs →
            </a>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-slate-800 transition"
            aria-label="Close results"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Single scroll region — send/share + findings (avoids sticky header eating viewport) */}
        <div className="flex-1 min-h-0 overflow-y-auto px-5 sm:px-8 py-5 space-y-6">
          <div className="space-y-3 pb-2 border-b border-emerald-500/30">
            <SendResultsForm
              researchId={effectiveResearchId}
              summary={summary}
              analysis={analysis}
              defaultEmail={defaultEmail}
              defaultPhone={defaultPhone}
            />

            <div>
              <p className="text-xs font-bold uppercase tracking-wide text-purple-300/90 mb-2 flex items-center gap-2">
                <Share2 className="w-3.5 h-3.5" />
                Share results
              </p>
              {(analysis.share_url || effectiveResearchId) && (
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <a
                    href={analysis.share_url || `${APP_URL}r/${effectiveResearchId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-3 py-2 min-h-[44px] rounded-lg border border-amber-500/40 bg-amber-500/10 text-amber-100 text-sm font-semibold hover:bg-amber-500/20 transition"
                  >
                    Open bid-file report
                  </a>
                  <button
                    type="button"
                    onClick={async () => {
                      const url = analysis.share_url || `${APP_URL}r/${effectiveResearchId}`;
                      await navigator.clipboard.writeText(url);
                      showToast('Share link copied — paste into your bid file or GC email');
                    }}
                    className="inline-flex items-center gap-2 px-3 py-2 min-h-[44px] rounded-lg border border-slate-600 bg-slate-800/80 text-gray-200 text-sm font-semibold hover:bg-slate-700 transition"
                  >
                    Copy /r/ link
                  </button>
                </div>
              )}
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={openWhatsApp}
                  className="inline-flex items-center gap-2 px-3 py-2 min-h-[44px] rounded-lg border border-emerald-500/40 bg-emerald-500/10 text-emerald-200 text-sm font-semibold hover:bg-emerald-500/20 transition"
                >
                  WhatsApp
                </button>
                <button
                  type="button"
                  onClick={() => void openFacebook()}
                  className="inline-flex items-center gap-2 px-3 py-2 min-h-[44px] rounded-lg border border-blue-500/40 bg-blue-500/10 text-blue-200 text-sm font-semibold hover:bg-blue-500/20 transition"
                >
                  Facebook
                </button>
                <button
                  type="button"
                  onClick={() => void openInstagram()}
                  className="inline-flex items-center gap-2 px-3 py-2 min-h-[44px] rounded-lg border border-pink-500/40 bg-pink-500/10 text-pink-200 text-sm font-semibold hover:bg-pink-500/20 transition"
                >
                  Instagram
                </button>
                <button
                  type="button"
                  onClick={() => void copyShareText('text')}
                  className="inline-flex items-center gap-2 px-3 py-2 min-h-[44px] rounded-lg border border-purple-500/40 bg-purple-500/10 text-purple-200 text-sm font-semibold hover:bg-purple-500/20 transition"
                >
                  {copied === 'text' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  {copied === 'text' ? 'Copied' : 'Copy'}
                </button>
                <button
                  type="button"
                  onClick={() => void copyShareText('facebook')}
                  className="inline-flex items-center gap-2 px-3 py-2 min-h-[44px] rounded-lg border border-slate-600 bg-slate-800/80 text-gray-200 text-sm font-semibold hover:bg-slate-700 transition"
                >
                  {copied === 'facebook' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  {copied === 'facebook' ? 'Copied for Facebook' : 'Copy for Facebook'}
                </button>
              </div>
              {toast && (
                <p className="mt-2 text-sm text-emerald-300" role="status">
                  {toast}
                </p>
              )}
            </div>
          </div>

          {(hideRisk || unverifiedEstimates) && (
            <div
              className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-100"
              role="status"
            >
              <p className="font-semibold text-amber-50 mb-1">Honesty notice</p>
              <p>{honestyLabels?.risk || 'Environmental risk scores are not parcel-verified GIS data. Do not use for bidding.'}</p>
              <p className="mt-1">{honestyLabels?.cost || 'Dollar and day figures are unverified estimates — confirm with the AHJ.'}</p>
            </div>
          )}

          {/* Summary cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-blue-600/20 border border-blue-500/30 rounded-lg p-4">
              <div className="text-2xl font-black text-blue-400">
                {analysis.summary.total_environmental_risks}
              </div>
              <p className="text-gray-300 text-sm">Checklist topics</p>
            </div>
            <div className="bg-orange-600/20 border border-orange-500/30 rounded-lg p-4">
              <div className="text-2xl font-black text-orange-400">
                {hideRisk ? '—' : analysis.summary.high_risk_count}
              </div>
              <p className="text-gray-300 text-sm">
                {hideRisk ? 'Verified high risks' : 'High/Critical Risks'}
              </p>
            </div>
            <div
              className={`border rounded-lg p-4 ${
                hideRisk
                  ? 'bg-amber-600/20 border-amber-500/30'
                  : analysis.environmental_screening.risk_level === 'LOW'
                    ? 'bg-green-600/20 border-green-500/30'
                    : analysis.environmental_screening.risk_level === 'MEDIUM'
                      ? 'bg-yellow-600/20 border-yellow-500/30'
                      : 'bg-red-600/20 border-red-500/30'
              }`}
            >
              <div
                className={`text-xl font-black ${
                  hideRisk
                    ? 'text-amber-300'
                    : analysis.environmental_screening.risk_level === 'LOW'
                      ? 'text-green-400'
                      : analysis.environmental_screening.risk_level === 'MEDIUM'
                        ? 'text-yellow-400'
                        : 'text-red-400'
                }`}
              >
                {hideRisk ? 'Unavailable' : `${analysis.environmental_screening.risk_level} Risk`}
              </div>
              <p className="text-gray-300 text-sm">
                {hideRisk ? 'Risk score (not verified)' : 'Overall Assessment'}
              </p>
            </div>
          </div>

          {/* Environmental findings */}
          <section>
            <button
              type="button"
              onClick={() => toggle('environmental')}
              className="w-full flex items-center justify-between bg-purple-600/20 border border-purple-500/30 rounded-lg p-4 mb-3"
            >
              <h3 className="text-lg font-bold text-white">
                {hideRisk ? 'Preliminary checklist notes' : 'Environmental Findings'}
              </h3>
              {expanded.environmental ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>
            {expanded.environmental && (
              <div className="space-y-3">
                {(analysis.environmental_screening.findings || []).length === 0 ? (
                  <p className="text-sm text-gray-400 border border-slate-700/60 rounded-lg p-4">
                    No checklist notes in this preview yet. Scroll this panel or re-run after the API
                    deploy includes full free-trial analysis.
                  </p>
                ) : (
                  (analysis.environmental_screening.findings || []).slice(0, 8).map((finding, idx) => (
                    <div key={idx} className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2 gap-2">
                        <h4 className="font-bold text-white capitalize">
                          {(finding.category || 'note').replace(/_/g, ' ')}
                        </h4>
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-semibold ${
                            hideRisk || finding.risk_level === 'PRELIMINARY'
                              ? 'text-amber-800 bg-amber-50'
                              : getRiskColor(finding.risk_level)
                          }`}
                        >
                          {hideRisk || finding.risk_level === 'PRELIMINARY'
                            ? 'PRELIMINARY'
                            : finding.risk_level}
                        </span>
                      </div>
                      <p className="text-gray-300 text-sm mb-2">{finding.description}</p>
                      {(finding.action_items || []).length > 0 && (
                        <ul className="space-y-1">
                          {finding.action_items.slice(0, 3).map((item, i) => (
                            <li key={i} className="text-xs text-gray-400 flex gap-2">
                              <span className="text-purple-400">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </section>

          {/* AHJ inspection sequence (DFW / Austin catalog) */}
          {(analysis.punch_list?.inspection_sequence || analysis.summary?.inspection_sequence || []).length >
            0 && (
            <section className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-4">
              <h3 className="text-sm font-bold text-gray-300 mb-2">Inspection sequence</h3>
              <ol className="list-decimal list-inside space-y-1 text-sm text-gray-200">
                {(
                  analysis.punch_list?.inspection_sequence ||
                  analysis.summary?.inspection_sequence ||
                  []
                ).map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </section>
          )}

          {/* Critical path / punch list highlights */}
          <section>
            <button
              type="button"
              onClick={() => toggle('critical')}
              className="w-full flex items-center justify-between bg-red-600/20 border border-red-500/30 rounded-lg p-4 mb-3"
            >
              <h3 className="text-lg font-bold text-white">Punch List Highlights</h3>
              {expanded.critical ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>
            {expanded.critical && (
              <div className="space-y-2">
                {(analysis.punch_list?.critical_path || []).slice(0, 5).map((task, idx) => (
                  <div key={idx} className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                    <p className="text-gray-200 text-sm">
                      <span className="text-red-400 font-bold mr-2">{idx + 1}.</span>
                      {task}
                    </p>
                  </div>
                ))}
                {(analysis.punch_list?.punch_list || []).slice(0, 5).map((item, idx) => (
                  <div key={`pl-${idx}`} className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3">
                    <div className="flex justify-between gap-2 mb-1">
                      <p className="text-white text-sm font-semibold">{item.task}</p>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-semibold whitespace-nowrap ${getPriorityBadge(item.priority)}`}
                      >
                        {item.priority}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">
                      {item.timeline} • {item.responsible_party}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Timeline & cost */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-5">
              <div className="flex items-center justify-between gap-2 mb-2">
                <h3 className="text-sm font-bold text-gray-400">Timeline</h3>
                {unverifiedEstimates && (
                  <span className="text-[10px] font-bold uppercase tracking-wide text-amber-300 border border-amber-500/40 rounded px-1.5 py-0.5">
                    Unverified
                  </span>
                )}
              </div>
              <p className="text-2xl font-black text-blue-400">
                {analysis.summary.estimated_timeline}
              </p>
              {unverifiedEstimates && (
                <p className="text-xs text-amber-200/80 mt-2">
                  {honestyLabels?.timeline || 'Confirm with AHJ / utility — not a quoted schedule.'}
                </p>
              )}
            </div>
            <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-5">
              <div className="flex items-center justify-between gap-2 mb-2">
                <h3 className="text-sm font-bold text-gray-400">Estimated Cost</h3>
                {unverifiedEstimates && (
                  <span className="text-[10px] font-bold uppercase tracking-wide text-amber-300 border border-amber-500/40 rounded px-1.5 py-0.5">
                    Unverified
                  </span>
                )}
              </div>
              <p className="text-2xl font-black text-green-400">
                ${(analysis.summary.estimated_total_cost || 0).toLocaleString()}
              </p>
              {unverifiedEstimates && (
                <p className="text-xs text-amber-200/80 mt-2">
                  {honestyLabels?.cost || 'Not an AHJ fee quote — confirm before bidding.'}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
