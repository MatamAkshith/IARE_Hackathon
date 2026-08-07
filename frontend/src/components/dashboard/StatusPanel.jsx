import React from 'react'

/**
 * Service Readiness monitor panel.
 * Displays offline placeholders for pipeline components in the static phase.
 * 
 * @param {Object} props
 * @param {Array} props.services Service status variables list
 */
export default function StatusPanel({ services = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Ready Engine Monitors</h3>
      </div>

      <div className="space-y-3">
        {services.map((srv, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between p-2.5 rounded bg-[#0d1322]/55 border border-[#141d2e] hover:border-[#1e293b] transition-colors"
          >
            <span className="text-xs text-slate-400 font-medium font-sans">
              {srv.name}
            </span>
            <div className="flex items-center gap-2">
              <span className={`w-1.5 h-1.5 rounded-full ${srv.color} animate-pulse`} />
              <span className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest">
                {srv.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
