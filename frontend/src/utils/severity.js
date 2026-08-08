/**
 * Shared Severity Utility — Hotfix H.2
 * 
 * Enforces uniform Green/Yellow/Red severity mappings globally.
 */

export function getSeverity(score) {
  const numericScore = Number(score)
  if (isNaN(numericScore)) return 'UNKNOWN'
  if (numericScore <= 20) return 'SAFE'
  if (numericScore <= 70) return 'MEDIUM'
  if (numericScore <= 90) return 'HIGH'
  return 'CRITICAL'
}

export function getSeverityColor(score) {
  const severity = getSeverity(score)
  if (severity === 'SAFE') return '#10b981' // Green (emerald-500)
  if (severity === 'MEDIUM') return '#eab308' // Yellow (amber-500)
  if (severity === 'HIGH' || severity === 'CRITICAL') return '#f43f5e' // Red (rose-500)
  return '#94a3b8' // Slate fallback
}

export function getSeverityBadge(score) {
  const severity = getSeverity(score)
  if (severity === 'SAFE') {
    return 'bg-emerald-950/30 text-emerald-400 border-emerald-800/40'
  }
  if (severity === 'MEDIUM') {
    return 'bg-amber-950/30 text-amber-400 border-amber-800/40'
  }
  if (severity === 'HIGH' || severity === 'CRITICAL') {
    return 'bg-rose-950/30 text-rose-400 border-rose-800/40'
  }
  return 'bg-slate-950/30 text-slate-400 border-slate-800/40'
}
