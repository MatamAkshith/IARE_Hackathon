import { getSeverityDetails } from '../../utils/severityUtils'

/**
 * Chronological SOC Threat Activity log timeline.
 * 
 * @param {Object} props
 * @param {Array} props.events Timeline events array
 */
export default function ThreatTimeline({ events = [] }) {
  const dotColor = (type) => {
    const details = getSeverityDetails(type)
    if (details.label === 'SAFE') {
      return 'bg-emerald-500 ring-emerald-500/20'
    }
    if (details.label === 'MEDIUM') {
      return 'bg-amber-500 ring-amber-500/20'
    }
    if (details.label === 'HIGH' || details.label === 'CRITICAL') {
      return 'bg-rose-500 ring-rose-500/20'
    }
    return 'bg-sky-500 ring-sky-500/20'
  }

  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">SOC Threat Activity Log</h3>
      </div>

      {/* Vertical list of events */}
      <div className="relative pl-4 space-y-5 border-l border-slate-800 ml-1.5 py-1">
        {events.length > 0 ? (
          events.map((event, idx) => (
            <div key={idx} className="relative group">
              {/* Timeline dot */}
              <span className={`absolute -left-[20px] top-1.5 w-2 h-2 rounded-full ring-4 ${dotColor(event.type)}`} />
              
              {/* Event card */}
              <div className="space-y-0.5">
                <span className="inline-block text-[10px] font-mono text-slate-500 font-bold tracking-wide">
                  TIME: {event.time}
                </span>
                <p className="text-xs text-slate-300 font-sans leading-relaxed break-words font-medium">
                  {event.message}
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-6 text-slate-500 text-xs font-medium">
            No events logged.
          </div>
        )}
      </div>
    </div>
  )
}
