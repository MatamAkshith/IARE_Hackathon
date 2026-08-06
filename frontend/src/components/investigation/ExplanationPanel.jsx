import React from 'react'

/**
 * Analyst Narrative Explanation list panel.
 * 
 * @param {Object} props
 * @param {Array} props.findings Bullet list of warning descriptions from dataset
 */
export default function ExplanationPanel({ findings = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4 shadow-md">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Threat Scoring Explanation</h3>
      </div>

      <ul className="space-y-3">
        {findings.map((finding, idx) => (
          <li key={idx} className="flex gap-2.5 items-start text-xs text-slate-300 leading-relaxed font-sans font-medium">
            <span className="text-rose-400 mt-0.5 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </span>
            <span>{finding}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
