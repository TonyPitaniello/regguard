/**
 * ResultsPage.tsx
 * Option A MVP: Displays comprehensive analysis results
 * Shows environmental risks + punch list after free trial submission
 */

import React, { useState, useEffect } from 'react';
import { AlertCircle, Download, ChevronDown, ChevronUp, Share2 } from 'lucide-react';
import ShareResultsModal from '../components/ShareResultsModal';

interface AnalysisData {
  timestamp: string;
  project_info: {
    address: string;
    city: string;
    state: string;
    zip: string;
    type: string;
    coordinates: { latitude: number; longitude: number };
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

export default function ResultsPage() {
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    environmental: true,
    punchList: true,
    critical: true,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [shareModal, setShareModal] = useState<{ isOpen: boolean; method: 'sms' | 'email' }>({
    isOpen: false,
    method: 'sms',
  });

  useEffect(() => {
    // Load analysis from session storage or route params
    const stored = sessionStorage.getItem('analysisResults');
    if (stored) {
      try {
        setAnalysis(JSON.parse(stored));
        setLoading(false);
      } catch (e) {
        setError('Failed to load results');
        setLoading(false);
      }
    } else {
      setError('No analysis results found. Please run the free trial first.');
      setLoading(false);
    }
  }, []);

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const getRiskColor = (level: string) => {
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
  };

  const getPriorityBadge = (priority: string) => {
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
  };

  const downloadResults = () => {
    if (!analysis) return;
    
    const dataStr = JSON.stringify(analysis, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `regguard-analysis-${analysis.project_info.zip}.json`;
    link.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading your analysis...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6 max-w-md">
          <AlertCircle className="w-6 h-6 text-red-500 mb-4" />
          <p className="text-red-200">{error || 'Failed to load analysis'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-6xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-black text-white mb-2">
            Your Site Diligence Analysis
          </h1>
          <p className="text-gray-400">
            {analysis.project_info.address} • {analysis.project_info.city}, {analysis.project_info.state} {analysis.project_info.zip}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Analysis completed: {new Date(analysis.timestamp).toLocaleDateString()}
          </p>
        </div>

        {/* Risk Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-gradient-to-br from-blue-600/20 to-blue-900/20 border border-blue-500/30 rounded-lg p-6">
            <div className="text-3xl font-black text-blue-400 mb-2">
              {analysis.summary.total_environmental_risks}
            </div>
            <p className="text-gray-300">Environmental Issues Found</p>
          </div>
          <div className="bg-gradient-to-br from-orange-600/20 to-orange-900/20 border border-orange-500/30 rounded-lg p-6">
            <div className="text-3xl font-black text-orange-400 mb-2">
              {analysis.summary.high_risk_count}
            </div>
            <p className="text-gray-300">High/Critical Risks</p>
          </div>
          <div className={`bg-gradient-to-br ${
            analysis.environmental_screening.risk_level === 'LOW'
              ? 'from-green-600/20 to-green-900/20 border-green-500/30'
              : analysis.environmental_screening.risk_level === 'MEDIUM'
              ? 'from-yellow-600/20 to-yellow-900/20 border-yellow-500/30'
              : 'from-red-600/20 to-red-900/20 border-red-500/30'
          } border rounded-lg p-6`}>
            <div className={`text-2xl font-black mb-2 ${
              analysis.environmental_screening.risk_level === 'LOW'
                ? 'text-green-400'
                : analysis.environmental_screening.risk_level === 'MEDIUM'
                ? 'text-yellow-400'
                : 'text-red-400'
            }`}>
              {analysis.environmental_screening.risk_level} Risk
            </div>
            <p className="text-gray-300">Overall Assessment</p>
          </div>
        </div>

        {/* Environmental Findings */}
        <section className="mb-8">
          <button
            onClick={() => toggleSection('environmental')}
            className="w-full flex items-center justify-between bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-lg p-6 mb-4 hover:border-purple-500/50 transition"
          >
            <h2 className="text-2xl font-bold text-white">Environmental Findings</h2>
            {expandedSections.environmental ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expandedSections.environmental && (
            <div className="space-y-4">
              {analysis.environmental_screening.findings.map((finding, idx) => (
                <div
                  key={idx}
                  className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-lg font-bold text-white capitalize">
                      {finding.category.replace(/_/g, ' ')}
                    </h3>
                    <span className={`px-3 py-1 rounded text-sm font-semibold ${getRiskColor(finding.risk_level)}`}>
                      {finding.risk_level}
                    </span>
                  </div>
                  <p className="text-gray-300 mb-4">{finding.description}</p>

                  <div className="mb-4">
                    <p className="text-sm font-semibold text-gray-400 mb-2">Action Items:</p>
                    <ul className="space-y-2">
                      {finding.action_items.map((item, i) => (
                        <li key={i} className="text-sm text-gray-300 flex items-start">
                          <span className="mr-3 text-purple-400">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Research Cost: ${finding.research_cost_usd}</span>
                    <span>{finding.data_sources.length} sources</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Critical Path */}
        <section className="mb-8">
          <button
            onClick={() => toggleSection('critical')}
            className="w-full flex items-center justify-between bg-gradient-to-r from-red-600/20 to-orange-600/20 border border-red-500/30 rounded-lg p-6 mb-4 hover:border-red-500/50 transition"
          >
            <h2 className="text-2xl font-bold text-white">Critical Path (Top Priority)</h2>
            {expandedSections.critical ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expandedSections.critical && (
            <div className="space-y-3">
              {analysis.punch_list.critical_path.map((task, idx) => (
                <div key={idx} className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                  <div className="flex items-start">
                    <span className="text-red-400 font-bold mr-3">{idx + 1}.</span>
                    <p className="text-gray-200">{task}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Full Punch List */}
        <section className="mb-8">
          <button
            onClick={() => toggleSection('punchList')}
            className="w-full flex items-center justify-between bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-lg p-6 mb-4 hover:border-green-500/50 transition"
          >
            <div>
              <h2 className="text-2xl font-bold text-white">Full Action Plan</h2>
              <p className="text-sm text-gray-400 mt-1">
                {analysis.summary.total_punch_list_items} items • Est. {analysis.summary.estimated_timeline}
              </p>
            </div>
            {expandedSections.punchList ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expandedSections.punchList && (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {analysis.punch_list.punch_list.slice(0, 20).map((item, idx) => (
                <div key={idx} className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-white font-semibold flex-1">{item.task}</p>
                    <span className={`px-2 py-1 rounded text-xs font-semibold whitespace-nowrap ml-2 ${getPriorityBadge(item.priority)}`}>
                      {item.priority}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                    <span>📅 {item.timeline}</span>
                    <span>👤 {item.responsible_party}</span>
                    {item.estimated_cost && <span>💰 ${item.estimated_cost.toLocaleString()}</span>}
                  </div>
                  {item.notes && <p className="text-xs text-gray-500 mt-2">{item.notes}</p>}
                </div>
              ))}
              {analysis.punch_list.punch_list.length > 20 && (
                <p className="text-center text-gray-400 text-sm py-4">
                  +{analysis.punch_list.punch_list.length - 20} more items in full report
                </p>
              )}
            </div>
          )}
        </section>

        {/* Timeline & Cost Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4">Timeline</h3>
            <p className="text-2xl font-black text-blue-400">
              {analysis.summary.estimated_timeline}
            </p>
            <p className="text-sm text-gray-400 mt-2">From submission to ready for construction</p>
          </div>
          <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4">Estimated Cost</h3>
            <p className="text-2xl font-black text-green-400">
              ${analysis.summary.estimated_total_cost.toLocaleString()}
            </p>
            <p className="text-sm text-gray-400 mt-2">Combined research + professional services</p>
          </div>
        </div>

        {/* Upgrade CTA */}
        <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Ready for the Full Report?</h2>
          <p className="text-gray-300 mb-6">
            This free analysis gives you key environmental findings and critical action items.
            Our <strong>premium package ($15,000)</strong> includes:
          </p>
          <ul className="space-y-2 mb-8 text-gray-300">
            <li className="flex items-center">
              <span className="text-purple-400 mr-3">✓</span>
              Professional punch list with contractor contacts
            </li>
            <li className="flex items-center">
              <span className="text-purple-400 mr-3">✓</span>
              State-specific permit application packages
            </li>
            <li className="flex items-center">
              <span className="text-purple-400 mr-3">✓</span>
              Utility interconnection timelines
            </li>
            <li className="flex items-center">
              <span className="text-purple-400 mr-3">✓</span>
              Same-day PDF delivery
            </li>
          </ul>

          <button
            onClick={() => window.location.href = '/pricing'}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-3 px-8 rounded-lg transition transform hover:scale-105"
          >
            Upgrade to Full Report ($15,000)
          </button>
        </div>

        {/* Share & Save Result */}
        <section className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-bold text-white mb-4">💾 Save & Share Result</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => setShareModal({ isOpen: true, method: 'sms' })}
              className="bg-gradient-to-r from-blue-600/80 to-blue-700/80 hover:from-blue-600 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2 border border-blue-500/50"
            >
              <span>📱</span>
              Text This Result
            </button>
            <button
              onClick={() => setShareModal({ isOpen: true, method: 'email' })}
              className="bg-gradient-to-r from-indigo-600/80 to-indigo-700/80 hover:from-indigo-600 hover:to-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2 border border-indigo-500/50"
            >
              <span>📧</span>
              Email This Result
            </button>
            <button
              onClick={downloadResults}
              className="bg-gradient-to-r from-purple-600/80 to-purple-700/80 hover:from-purple-600 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2 border border-purple-500/50"
            >
              <Download size={18} />
              Download PDF
            </button>
          </div>
        </section>

        {/* Actions */}
        <div className="flex gap-4 justify-center">
          <button
            onClick={downloadResults}
            className="bg-slate-800 hover:bg-slate-700 text-white font-semibold py-2 px-6 rounded-lg border border-slate-700 hover:border-slate-600 transition flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Download JSON
          </button>
          <button
            onClick={() => window.print()}
            className="bg-slate-800 hover:bg-slate-700 text-white font-semibold py-2 px-6 rounded-lg border border-slate-700 hover:border-slate-600 transition"
          >
            Print Results
          </button>
        </div>

        {/* Share Modal */}
        <ShareResultsModal
          isOpen={shareModal.isOpen}
          onClose={() => setShareModal({ isOpen: false, method: 'sms' })}
          deliveryMethod={shareModal.method}
          researchId="research-123"
          onSuccess={(result) => {
            console.log('Result shared successfully:', result);
          }}
        />
      </div>
    </div>
  );
}
