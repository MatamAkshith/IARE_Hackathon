import React from 'react'

/**
 * Visual badge for 0-100 risk scores matching the Risk Engine bands.
 * 
 * @param {Object} props
 * @param {number|null} props.score Risk score (0-100) or null
 */
export default function RiskScoreBadge({ score }) {
  if (score === undefined || score === null) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
        N/A
      </span>
    )
  }

  const numericScore = Number(score)

  let colorClasses = 'bg-slate-800 text-slate-400 border-slate-700'
  let label = 'Unknown'

  if (numericScore <= 20) {
    colorClasses = 'bg-emerald-950/20 text-emerald-400 border-emerald-800/40'
    label = 'Safe'
  } else if (numericScore <= 70) {
    colorClasses = 'bg-amber-950/20 text-amber-400 border-amber-800/40'
    label = 'Medium'
  } else if (numericScore <= 90) {
    colorClasses = 'bg-orange-950/20 text-orange-400 border-orange-800/40'
    label = 'High'
  } else {
    colorClasses = 'bg-rose-950/20 text-rose-400 border-rose-800/40'
    label = 'Critical'
  }

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded border text-[11px] font-semibold font-mono tracking-wide ${colorClasses}`}>
      <span>{numericScore}</span>
      <span className="opacity-50 text-[9px] uppercase font-sans font-bold">&bull; {label}</span>
    </span>
  )
}
