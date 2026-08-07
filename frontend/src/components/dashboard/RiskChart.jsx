import React from 'react'

/**
 * Custom Threat Risk distribution visualizer.
 * Renders a segmented horizontal telemetry bar without external chart libraries.
 * 
 * @param {Object} props
 * @param {Array} props.data Mapped distribution data list from dashboardData.js
 */
export default function RiskChart({ data = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-5">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 3.055A9.003 9.003 0 1 0 20.945 13H11V3.055z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.488 9H15V3.512A9.025 9.025 0 0 1 20.488 9z" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Threat Risk Distribution</h3>
      </div>

      {/* Segmented multi-color distribution bar */}
      <div className="h-3 w-full rounded-full bg-slate-800 flex overflow-hidden shadow-inner">
        {data.map((item, idx) => (
          <div
            key={idx}
            style={{ width: `${item.percentage}%` }}
            className={`${item.color} transition-all duration-500`}
            title={`${item.label}: ${item.count} (${item.percentage}%)`}
          />
        ))}
      </div>

      {/* Grid details legend */}
      <div className="grid grid-cols-2 gap-4">
        {data.map((item, idx) => (
          <div
            key={idx}
            className="p-3 bg-[#0d1322]/55 border border-[#141d2e] rounded-lg space-y-1 hover:border-[#223049] transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${item.color.replace('bg-', 'bg-')}`} />
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                {item.label.split(' ')[0]}
              </span>
            </div>
            <div className="flex justify-between items-baseline mt-1 font-mono">
              <span className="text-sm font-black text-slate-100">{item.count}</span>
              <span className="text-[10px] text-slate-500 font-semibold">{item.percentage}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
