import React from 'react'

/**
 * Risk metrics highlight panel for investigation targets.
 * 
 * @param {Object} props
 * @param {Object} props.risk Risk scoring dataset { score, maxScore, level, recommendation, confidence, badgeColor }
 */
export default function RiskSummary({ risk = {} }) {
  const isCritical = risk.level === 'Critical'
  const isHigh = risk.level === 'High'

  const borderClass = isCritical
    ? 'border-rose-900 bg-rose-950/10 text-rose-400 shadow-rose-500/5'
    : isHigh
    ? 'border-amber-900 bg-amber-950/10 text-amber-400 shadow-amber-500/5'
    : 'border-[#1a2336] bg-[#090d16] text-slate-300'

  return (
    <div className={`border p-5 rounded-xl shadow-md flex items-center justify-between gap-6 transition-all duration-300 ${borderClass}`}>
      <div className="space-y-3.5">
        <div className="space-y-1">
          <span className="block text-[9px] uppercase font-extrabold tracking-widest text-slate-500">
            Threat Evaluation
          </span>
          <div className="flex items-baseline gap-2">
            <h3 className={`text-2xl font-black font-sans uppercase tracking-tight`}>
              {risk.level} Severity
            </h3>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-xs">
          <div>
            <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">
              Analyst Action
            </span>
            <span className="font-semibold text-slate-200 block truncate">{risk.recommendation}</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">
              Scoring Confidence
            </span>
            <span className="font-semibold text-slate-200 block truncate font-mono">{risk.confidence}</span>
          </div>
        </div>
      </div>

      {/* Large Score Circular Metric */}
      <div className="relative flex items-center justify-center flex-shrink-0">
        <svg className="w-20 h-20 transform -rotate-90">
          <circle
            className="text-slate-800"
            strokeWidth="5"
            stroke="currentColor"
            fill="transparent"
            r="32"
            cx="40"
            cy="40"
          />
          <circle
            className={isCritical ? 'text-rose-500' : isHigh ? 'text-amber-500' : 'text-emerald-500'}
            strokeWidth="5"
            strokeDasharray={2 * Math.PI * 32}
            strokeDashoffset={2 * Math.PI * 32 * (1 - risk.score / 100)}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r="32"
            cx="40"
            cy="40"
          />
        </svg>
        <div className="absolute text-center">
          <span className="text-xl font-black font-mono tracking-tighter text-slate-100">
            {risk.score}
          </span>
          <span className="block text-[7px] uppercase tracking-wider text-slate-500 mt-[-2px]">Score</span>
        </div>
      </div>
    </div>
  )
}
