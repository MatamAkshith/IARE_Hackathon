import React from 'react'

/**
 * Attribution Confidence & Severity dashboard panel.
 * 
 * @param {Object} props
 * @param {Object} props.confidence Confidence stats object from dataset
 */
export default function ConfidenceCard({ confidence = {} }) {
  return (
    <div className="border border-rose-900 bg-rose-950/10 p-5 rounded-xl shadow-md flex items-center justify-between gap-6 transition-all duration-300">
      <div className="space-y-3.5 min-w-0 flex-1">
        <div className="space-y-1">
          <span className="block text-[9px] uppercase font-extrabold tracking-widest text-slate-500">
            Attribution Engine Verdict
          </span>
          <h3 className="text-xl font-black text-rose-400 uppercase tracking-tight truncate">
            {confidence.severity} Severity Alert
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-xs">
          <div>
            <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Correlated Domains</span>
            <span className="font-semibold text-slate-200 block truncate">{confidence.correlatedDomains} active targets</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Shared IOCs</span>
            <span className="font-semibold text-slate-200 block truncate">{confidence.sharedIndicators} matching points</span>
          </div>
          <div className="col-span-2 mt-1">
            <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Mitigation Recommendation</span>
            <p className="font-medium text-slate-300 mt-0.5 leading-relaxed">{confidence.recommendation}</p>
          </div>
        </div>
      </div>

      {/* Confidence radial or text block */}
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
            strokeDashoffset={2 * Math.PI * 32 * (1 - confidence.score / 100)}
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
            {confidence.score}%
          </span>
          <span className="block text-[6.5px] uppercase tracking-wider text-slate-500 mt-[-2px]">Confidence</span>
        </div>
      </div>
    </div>
  )
}
