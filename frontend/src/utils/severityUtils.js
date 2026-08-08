/**
 * Unified Risk Severity Color Mapping Utility — Hotfix G.7
 * Maps risk scores and labels to uniform Green/Yellow/Red themes.
 */

export const getSeverityDetails = (scoreOrLabel) => {
  let score = null;
  let label = '';

  if (scoreOrLabel !== null && scoreOrLabel !== undefined && scoreOrLabel !== '') {
    if (typeof scoreOrLabel === 'number' || !isNaN(scoreOrLabel)) {
      score = Number(scoreOrLabel);
      if (score <= 20) {
        label = 'SAFE';
      } else if (score <= 70) {
        label = 'MEDIUM';
      } else if (score <= 90) {
        label = 'HIGH';
      } else {
        label = 'CRITICAL';
      }
    } else {
      label = String(scoreOrLabel).toUpperCase();
    }
  }

  // Normalize labels
  if (label === 'SAFE' || label === 'LOW' || label === 'GREEN') {
    return {
      label: 'SAFE',
      color: '#10b981', // Green (emerald-500)
      badgeClass: 'bg-emerald-950/30 text-emerald-400 border-emerald-800/40',
      textClass: 'text-emerald-400',
      bgClass: 'bg-emerald-500',
      borderClass: 'border-emerald-800/40',
      score: score
    };
  } else if (label === 'MEDIUM' || label === 'YELLOW' || label === 'WARN' || label === 'WARNING') {
    return {
      label: 'MEDIUM',
      color: '#eab308', // Yellow (amber-500)
      badgeClass: 'bg-amber-950/30 text-amber-400 border-amber-800/40',
      textClass: 'text-amber-400',
      bgClass: 'bg-amber-500',
      borderClass: 'border-amber-800/40',
      score: score
    };
  } else if (label === 'HIGH' || label === 'CRITICAL' || label === 'RED') {
    return {
      label: label === 'HIGH' ? 'HIGH' : 'CRITICAL',
      color: '#f43f5e', // Red (rose-500)
      badgeClass: 'bg-rose-950/30 text-rose-400 border-rose-800/40',
      textClass: 'text-rose-400',
      bgClass: 'bg-rose-500',
      borderClass: 'border-rose-800/40',
      score: score
    };
  }

  // Default fallback (Slate)
  return {
    label: label || 'UNKNOWN',
    color: '#94a3b8', // slate-400
    badgeClass: 'bg-slate-950/30 text-slate-400 border-slate-800/40',
    textClass: 'text-slate-400',
    bgClass: 'bg-slate-500',
    borderClass: 'border-slate-800/40',
    score: score
  };
};
