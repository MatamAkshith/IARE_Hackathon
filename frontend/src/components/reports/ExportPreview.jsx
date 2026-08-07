import React from 'react'

/**
 * Report Export shortcuts panel.
 * Displays static preview formats that are disabled in frontend sandbox mode.
 * 
 * @param {Object} props
 * @param {Array} props.options Mock export formats options list from dataset
 */
export default function ExportPreview({ options = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4 shadow-md w-full min-w-0 overflow-hidden">
      <div className="flex items-center justify-between border-b border-[#1a2336]/60 pb-3 gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <svg className="w-5 h-5 text-brand-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <h3 className="font-semibold text-slate-200 text-sm tracking-wide truncate">Export Incident Formats</h3>
        </div>
        <span className="text-[8px] font-mono font-bold uppercase text-slate-500 bg-slate-900 px-2 py-0.5 border border-slate-800 rounded flex-shrink-0">
          Sandbox Mode
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {options.map((opt) => (
          <button
            key={opt.id}
            type="button"
            disabled
            className="p-3 bg-[#0d1322]/55 border border-[#141d2e] rounded-lg text-left space-y-1 hover:border-[#1e283b] transition-all cursor-not-allowed group"
            title="Download option disabled in static preview mode."
          >
            <div className="flex justify-between items-center gap-1.5 min-w-0">
              <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide truncate group-hover:text-slate-300">
                {opt.name}
              </span>
              <svg className="w-3.5 h-3.5 text-slate-600 flex-shrink-0 group-hover:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <span className="block text-[9px] text-slate-650 leading-tight">
              {opt.desc}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
