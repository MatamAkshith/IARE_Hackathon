import React from 'react'

/**
 * KPI Summary Card component with standardized hover glows and responsive styling.
 * 
 * @param {Object} props
 * @param {string} props.title The metric label
 * @param {string|number} props.value The current total metric value
 * @param {Object} [props.trend] Optional trend data { value, positive }
 * @param {React.ReactNode} props.icon SVG markup icon
 * @param {Function} [props.onClick] Optional click handler for navigation
 */
export default function KPICard({ title, value, trend, icon, onClick }) {
  const interactiveClass = onClick ? 'cursor-pointer select-none' : ''

  return (
    <div
      className={`p-5 rounded-xl border border-slate-800/60 bg-[#090d16] flex items-center justify-between transition-all duration-200 hover:-translate-y-0.5 hover:border-brand-500 hover:shadow-[0_0_15px_rgba(14,165,233,0.15)] ${interactiveClass} group`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      <div className="space-y-1.5 min-w-0">
        <span className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest truncate group-hover:text-slate-400 transition-colors">
          {title}
        </span>
        <span className="block text-2xl font-black font-mono tracking-tight text-slate-100 mt-1 truncate">
          {value}
        </span>
        {trend && (
          <div className="flex items-center gap-1 mt-1 text-[10px]">
            <span className={`font-semibold ${trend.positive ? 'text-emerald-500' : 'text-rose-500'}`}>
              {trend.value}
            </span>
            <span className="text-slate-500 font-medium">vs last week</span>
          </div>
        )}
      </div>

      <div className="p-3 rounded-lg bg-[#0e1422] border border-[#1a2336] text-slate-400 group-hover:text-brand-400 group-hover:border-brand-500/35 transition-all duration-200">
        {icon}
      </div>
    </div>
  )
}
