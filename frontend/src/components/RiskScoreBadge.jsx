import React from 'react'
import { getSeverityDetails } from '../utils/severityUtils'

/**
 * Visual badge for 0-100 risk scores matching the Risk Engine bands.
 * 
 * @param {Object} props
 * @param {number|null} props.score Risk score (0-100) or null
 */
export default function RiskScoreBadge({ score }) {
  if (score === undefined || score === null) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded border text-[10px] font-semibold bg-blue-950/20 text-blue-400 border-blue-800/40">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
        PENDING
      </span>
    )
  }

  const numericScore = Number(score)
  const details = getSeverityDetails(numericScore)

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded border text-[11px] font-semibold font-mono tracking-wide ${details.badgeClass}`}>
      <span>{numericScore}</span>
      <span className="opacity-50 text-[9px] uppercase font-sans font-bold">&bull; {details.label}</span>
    </span>
  )
}
