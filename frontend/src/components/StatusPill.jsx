import React from 'react'

/**
 * Status indicator pill with active pulse triggers.
 * 
 * @param {Object} props
 * @param {string} props.status Status label string
 */
export default function StatusPill({ status }) {
  const normalized = status ? status.toLowerCase() : 'unknown'

  const styles = {
    pending: 'bg-blue-950/20 text-blue-400 border-blue-900/30 animate-pulse',
    processing: 'bg-sky-950/20 text-sky-400 border-sky-900/30 animate-pulse',
    completed: 'bg-emerald-950/20 text-emerald-400 border-emerald-900/30',
    success: 'bg-emerald-950/20 text-emerald-400 border-emerald-900/30',
    failed: 'bg-rose-950/20 text-rose-400 border-rose-900/30',
    error: 'bg-rose-950/20 text-rose-400 border-rose-900/30',
    unknown: 'bg-slate-800/30 text-slate-400 border-slate-700/30'
  }

  const currentStyle = styles[normalized] || styles.unknown

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider ${currentStyle}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {normalized}
    </span>
  )
}
