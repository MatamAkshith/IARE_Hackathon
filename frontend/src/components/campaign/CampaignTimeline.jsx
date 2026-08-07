import React from 'react'

/**
 * Attacker Cluster Deployment logs timeline.
 * 
 * @param {Object} props
 * @param {Array} props.timeline Timeline logs array from dataset
 */
export default function CampaignTimeline({ timeline = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4 shadow-md w-full min-w-0 overflow-hidden">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Campaign Activity History</h3>
      </div>

      {/* Vertical list of events */}
      <div className="relative pl-4 space-y-5 border-l border-slate-800 ml-1.5 py-1">
        {timeline.map((event, idx) => (
          <div key={idx} className="relative group w-full min-w-0">
            {/* Timeline dot */}
            <span className="absolute -left-[20px] top-1.5 w-2 h-2 rounded-full ring-4 bg-brand-500 ring-brand-500/20" />
            
            {/* Event detail */}
            <div className="space-y-0.5 w-full min-w-0">
              <span className="inline-block text-[10px] font-mono text-slate-500 font-bold tracking-wide">
                {event.time}
              </span>
              <span className="block text-xs font-bold text-slate-300 uppercase tracking-wide">
                {event.title}
              </span>
              <p className="text-xs text-slate-400 font-sans leading-relaxed break-words font-medium">
                {event.desc}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
