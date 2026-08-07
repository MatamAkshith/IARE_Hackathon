import React from 'react'

/**
 * Visual tags badge collection component.
 * 
 * @param {Object} props
 * @param {Array} props.badges Badges list from dataset
 */
export default function BadgeGroup({ badges = [] }) {
  const badgeStyles = {
    danger: 'bg-rose-950/20 text-rose-400 border-rose-800/40 shadow-rose-500/5',
    warning: 'bg-amber-950/20 text-amber-400 border-amber-800/40 shadow-amber-500/5',
    info: 'bg-brand-950/20 text-brand-400 border-brand-850/30 shadow-brand-500/5'
  }

  return (
    <div className="flex flex-wrap gap-2.5">
      {badges.map((badge, idx) => {
        const styleClass = badgeStyles[badge.type] || badgeStyles.info
        return (
          <span
            key={idx}
            className={`px-3 py-1 text-[10px] font-extrabold uppercase tracking-wider rounded border transition-colors ${styleClass}`}
          >
            {badge.label}
          </span>
        )
      })}
    </div>
  )
}
