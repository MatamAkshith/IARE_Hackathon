import { getSeverity, getSeverityColor, getSeverityBadge } from './severity'

export const getSeverityDetails = (scoreOrLabel) => {
  let score = null
  let label = ''

  if (scoreOrLabel !== null && scoreOrLabel !== undefined && scoreOrLabel !== '') {
    if (typeof scoreOrLabel === 'number' || !isNaN(scoreOrLabel)) {
      score = Number(scoreOrLabel)
      label = getSeverity(score)
    } else {
      label = String(scoreOrLabel).toUpperCase()
    }
  }

  // Normalize labels
  if (label === 'SAFE' || label === 'LOW' || label === 'GREEN') {
    return {
      label: 'SAFE',
      color: getSeverityColor(10),
      badgeClass: getSeverityBadge(10),
      textClass: 'text-emerald-400',
      bgClass: 'bg-emerald-500',
      borderClass: 'border-emerald-800/40',
      score: score
    }
  } else if (label === 'MEDIUM' || label === 'YELLOW' || label === 'WARN' || label === 'WARNING') {
    return {
      label: 'MEDIUM',
      color: getSeverityColor(50),
      badgeClass: getSeverityBadge(50),
      textClass: 'text-amber-400',
      bgClass: 'bg-amber-500',
      borderClass: 'border-amber-800/40',
      score: score
    }
  } else if (label === 'HIGH' || label === 'CRITICAL' || label === 'RED') {
    return {
      label: label === 'HIGH' ? 'HIGH' : 'CRITICAL',
      color: getSeverityColor(95),
      badgeClass: getSeverityBadge(95),
      textClass: 'text-rose-400',
      bgClass: 'bg-rose-500',
      borderClass: 'border-rose-800/40',
      score: score
    }
  }

  // Default fallback (Slate)
  return {
    label: label || 'UNKNOWN',
    color: '#94a3b8',
    badgeClass: 'bg-slate-950/30 text-slate-400 border-slate-800/40',
    textClass: 'text-slate-400',
    bgClass: 'bg-slate-500',
    borderClass: 'border-slate-800/40',
    score: score
  }
}

