/**
 * Shared honesty helpers for free-trial / preview analysis UI.
 */

export type HonestyMeta = {
  risk_verified?: boolean;
  cost_verified?: boolean;
  timeline_verified?: boolean;
  source?: string;
  labels?: {
    risk?: string;
    cost?: string;
    timeline?: string;
  };
};

export function isRiskScoreHidden(analysis: {
  preview?: boolean;
  honesty?: HonestyMeta;
  environmental_screening?: { risk_level?: string; risk_score_hidden?: boolean };
}): boolean {
  const honesty = analysis.honesty;
  if (honesty?.risk_verified === true) return false;
  const level = (analysis.environmental_screening?.risk_level || '').toUpperCase();
  if (['UNAVAILABLE', 'PRELIMINARY', 'UNKNOWN', ''].includes(level)) return true;
  if (analysis.environmental_screening?.risk_score_hidden) return true;
  if (analysis.preview && honesty?.risk_verified !== true) return true;
  return false;
}

export function areEstimatesUnverified(analysis: {
  preview?: boolean;
  honesty?: HonestyMeta;
  summary?: { estimates_unverified?: boolean; cost_verified?: boolean; timeline_verified?: boolean };
}): boolean {
  const honesty = analysis.honesty;
  if (honesty?.cost_verified === true && honesty?.timeline_verified === true) return false;
  if (analysis.summary?.estimates_unverified) return true;
  if (analysis.preview) return true;
  if (honesty && honesty.cost_verified === false) return true;
  return false;
}
