import React from 'react'

/**
 * Analyst Mitigation Recommendations panel.
 * 
 * @param {Object} props
 * @param {Array} props.recommendations Checklist of recommendations strings
 */
export default function RecommendationsPanel({ recommendations = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4 shadow-md w-full min-w-0 overflow-hidden">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">SOC Analyst Action Items</h3>
      </div>

      <ul className="space-y-3 w-full min-w-0">
        {recommendations.map((rec, idx) => (
          <li key={idx} className="flex gap-2.5 items-start text-xs text-slate-300 leading-relaxed font-sans font-medium w-full min-w-0">
            <span className="text-brand-400 mt-0.5 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2-2M9 5a2 2 0 002 2h2a2 2 0 002-2" />
              </svg>
            </span>
            <span className="break-words min-w-0 flex-1">{rec}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
