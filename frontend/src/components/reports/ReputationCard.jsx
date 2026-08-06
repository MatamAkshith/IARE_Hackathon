import React from 'react'

/**
 * Reputation Summary gauge panel.
 * 
 * @param {Object} props
 * @param {Object} props.reputation Reputation summary stats object from dataset
 */
export default function ReputationCard({ reputation = {} }) {
  return (
    <div className="border border-rose-900 bg-rose-950/10 p-5 rounded-xl shadow-md flex items-center justify-between gap-6 transition-all duration-300">
      <div className="space-y-3.5 min-w-0 flex-1">
        <div className="space-y-1">
          <span className="block text-[9px] uppercase font-extrabold tracking-widest text-slate-500">
            Reputation Evaluation
          </span>
          <h3 className="text-xl font-black text-rose-400 uppercase tracking-tight truncate">
            {reputation.verdict} Verdict
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-xs">
          <div>
            <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Risk Level</span>
            <span className="font-semibold text-slate-250 block truncate text-rose-400 font-sans uppercase">{reputation.riskLevel}</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Feed Confidence</span>
            <span className="font-semibold text-slate-200 block truncate font-mono">{reputation.confidence}</span>
          </div>
          <div className="col-span-2 mt-1">
            <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Mitigation Action</span>
            <span className="font-black text-rose-400 block mt-0.5 tracking-wide text-xs">{reputation.recommendation}</span>
          </div>
        </div>
      </div>

      {/* Radial score gauge */}
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
            className="text-rose-500"
            strokeWidth="5"
            strokeDasharray={2 * Math.PI * 32}
            strokeDashoffset={2 * Math.PI * 32 * (1 - reputation.score / 100)}
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
            {reputation.score}
          </span>
          <span className="block text-[7px] uppercase tracking-wider text-slate-500 mt-[-2px]">Score</span>
        </div>
      </div>
    </div>
  )
}
