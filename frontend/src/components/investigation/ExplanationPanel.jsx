import React from 'react'

/**
 * Analyst Narrative Explanation list panel.
 * 
 * @param {Object} props
 * @param {Array} props.findings Bullet list of warning descriptions from dataset
 */
export default function ExplanationPanel({ findings = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4 shadow-md w-full min-w-0 overflow-hidden">
      <div className="flex items-center gap-2.5 border-b border-[#1a2336]/60 pb-3 min-w-0">
        <svg className="w-5 h-5 text-brand-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7 a 2 2 0 0 1 -2 -2 V5 a 2 2 0 0 1 2 -2 h5.586 a 1 1 0 0 1 0.707 0.293 l5.414 5.414 a 1 1 0 0 1 0.293 0.707 V19 a 2 2 0 0 1 -2 2 z" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide truncate">Threat Scoring Explanation</h3>
      </div>

      <ul className="space-y-3 w-full min-w-0">
        {findings.map((finding, idx) => (
          <li key={idx} className="flex gap-2.5 items-start text-xs text-slate-300 leading-relaxed font-sans font-medium w-full min-w-0">
            <span className="text-rose-400 mt-0.5 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </span>
            <span className="break-words min-w-0 flex-1">{finding}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
