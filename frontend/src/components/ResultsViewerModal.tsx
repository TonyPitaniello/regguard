/**
 * ResultsViewerModal — large overlay showing free-trial analysis + text/email send.
 * Stays on the current page (homepage / free-trial); does not require /results navigation.
 */

import { useState } from 'react';
import { X, ChevronDown, ChevronUp } from 'lucide-react';
import SendResultsForm, { ResultsSummaryPayload } from './SendResultsForm';

export interface AnalysisData {
  timestamp: string;
  research_id?: string;
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
      notes: string;
    }>;
    timeline_summary: string;
    estimated_total_cost: number;
    critical_path: string[];
    milestones: Array<{ week: string; milestone: string }>;
    who_to_call: Record<string, string>;
  };
  summary: {
    total_environmental_risks: number;
    high_risk_count: number;
    total_punch_list_items: number;
    estimated_timeline: string;
    estimated_total_cost: number;
  };
  next_steps: string[];
}

interface ResultsViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  analysis: AnalysisData;
  researchId?: string | null;
  defaultEmail?: string;
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
  return {
    zip: analysis.project_info?.zip,
    city: analysis.project_info?.city,
    state: analysis.project_info?.state,
    address: analysis.project_info?.address,
    risk_level: analysis.environmental_screening?.risk_level,
    timeline: analysis.summary?.estimated_timeline,
    cost: analysis.summary?.estimated_total_cost,
  };
}

export default function ResultsViewerModal({
  isOpen,
  onClose,
  analysis,
  researchId,
  defaultEmail = '',
}: ResultsViewerModalProps) {
  const [expanded, setExpanded] = useState({
    environmental: true,
    punchList: true,
    critical: true,
  });

  if (!isOpen || !analysis) return null;

  const summary = buildSummaryFromAnalysis(analysis);
  const effectiveResearchId = researchId || analysis.research_id || null;

  const toggle = (key: keyof typeof expanded) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
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
        <div className="flex items-start justify-between gap-4 px-5 sm:px-8 py-5 border-b border-slate-700/80 bg-slate-900/90 sticky top-0 z-10">
          <div>
            <h2 id="results-modal-title" className="text-2xl sm:text-3xl font-black text-white">
              Your Site Diligence Analysis
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              {analysis.project_info.address} • {analysis.project_info.city},{' '}
              {analysis.project_info.state} {analysis.project_info.zip}
            </p>
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

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto px-5 sm:px-8 py-6 space-y-6">
          {/* Summary cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-blue-600/20 border border-blue-500/30 rounded-lg p-4">
              <div className="text-2xl font-black text-blue-400">
                {analysis.summary.total_environmental_risks}
              </div>
              <p className="text-gray-300 text-sm">Environmental Issues</p>
            </div>
            <div className="bg-orange-600/20 border border-orange-500/30 rounded-lg p-4">
              <div className="text-2xl font-black text-orange-400">
                {analysis.summary.high_risk_count}
              </div>
              <p className="text-gray-300 text-sm">High/Critical Risks</p>
            </div>
            <div
              className={`border rounded-lg p-4 ${
                analysis.environmental_screening.risk_level === 'LOW'
                  ? 'bg-green-600/20 border-green-500/30'
                  : analysis.environmental_screening.risk_level === 'MEDIUM'
                    ? 'bg-yellow-600/20 border-yellow-500/30'
                    : 'bg-red-600/20 border-red-500/30'
              }`}
            >
              <div
                className={`text-xl font-black ${
                  analysis.environmental_screening.risk_level === 'LOW'
                    ? 'text-green-400'
                    : analysis.environmental_screening.risk_level === 'MEDIUM'
                      ? 'text-yellow-400'
                      : 'text-red-400'
                }`}
              >
                {analysis.environmental_screening.risk_level} Risk
              </div>
              <p className="text-gray-300 text-sm">Overall Assessment</p>
            </div>
          </div>

          {/* Environmental findings */}
          <section>
            <button
              type="button"
              onClick={() => toggle('environmental')}
              className="w-full flex items-center justify-between bg-purple-600/20 border border-purple-500/30 rounded-lg p-4 mb-3"
            >
              <h3 className="text-lg font-bold text-white">Environmental Findings</h3>
              {expanded.environmental ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>
            {expanded.environmental && (
              <div className="space-y-3">
                {(analysis.environmental_screening.findings || []).slice(0, 8).map((finding, idx) => (
                  <div key={idx} className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2 gap-2">
                      <h4 className="font-bold text-white capitalize">
                        {finding.category.replace(/_/g, ' ')}
                      </h4>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-semibold ${getRiskColor(finding.risk_level)}`}
                      >
                        {finding.risk_level}
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
                ))}
              </div>
            )}
          </section>

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
              <h3 className="text-sm font-bold text-gray-400 mb-2">Timeline</h3>
              <p className="text-2xl font-black text-blue-400">
                {analysis.summary.estimated_timeline}
              </p>
            </div>
            <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-5">
              <h3 className="text-sm font-bold text-gray-400 mb-2">Estimated Cost</h3>
              <p className="text-2xl font-black text-green-400">
                ${(analysis.summary.estimated_total_cost || 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        {/* Sticky footer: send results */}
        <div className="border-t border-slate-700 bg-slate-900/95 px-5 sm:px-8 py-5">
          <SendResultsForm
            researchId={effectiveResearchId}
            summary={summary}
            defaultEmail={defaultEmail}
            compact
          />
        </div>
      </div>
    </div>
  );
}
