import React from 'react'

/**
 * KPI Summary Card component with hover glows and responsive styling.
 * 
 * @param {Object} props
 * @param {string} props.title The metric label
 * @param {string|number} props.value The current total metric value
 * @param {Object} [props.trend] Optional trend data { value, positive }
 * @param {React.ReactNode} props.icon SVG markup icon
 * @param {string} [props.type] Color coding style (neutral, warning, danger, success, info)
 * @param {Function} [props.onClick] Optional click handler for navigation
 */
export default function KPICard({ title, value, trend, icon, type = 'neutral', onClick }) {
  // Default state: subtle muted border and bg tint. Hover: full-brightness border + glow.
  // All cards follow the same pattern: default is dim, hover is bright.
  const typeClasses = {
    neutral: 'border-slate-800/50 hover:border-slate-600 hover:shadow-slate-700/20 text-slate-300',
    success: 'border-emerald-950 bg-emerald-950/10 text-emerald-400 hover:border-emerald-800/80 hover:shadow-emerald-500/10',
    info:    'border-brand-950 bg-brand-950/10 text-brand-400 hover:border-brand-800/80 hover:shadow-brand-500/10',
    warning: 'border-amber-950 bg-amber-950/10 text-amber-400 hover:border-amber-800/80 hover:shadow-amber-500/10',
    danger:  'border-rose-950 bg-rose-950/10 text-rose-400 hover:border-rose-800/80 hover:shadow-rose-500/10',
  }

  const borderClass = typeClasses[type] || typeClasses.neutral
  const interactiveClass = onClick ? 'cursor-pointer select-none' : ''

  return (
    <div
      className={`p-5 rounded-xl border bg-[#090d16] flex items-center justify-between transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg ${borderClass} ${interactiveClass} group`}
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

      <div className="p-3 rounded-lg bg-[#0e1422] border border-[#1a2336] text-slate-400 group-hover:text-brand-400 group-hover:border-brand-500/35 transition-all duration-300">
        {icon}
      </div>
    </div>
  )
}
