import React from 'react'

/**
 * Scan Telemetry tracking status card.
 * 
 * @param {Object} props
 * @param {'queued'|'scanning'|'completed'} props.status Current loading step
 */
export default function ScanStatus({ status }) {
  const steps = [
    { key: 'queued', label: 'Queued', desc: 'Pre-flight check & URL normalization' },
    { key: 'scanning', label: 'Scanning', desc: 'Ingesting WHOIS, DNS & HTML structure' },
    { key: 'completed', label: 'Completed', desc: 'Verdict compiled' }
  ]

  const getStepIndex = (key) => {
    if (key === 'queued') return 0
    if (key === 'scanning') return 1
    if (key === 'completed') return 2
    return -1
  }

  const currentIdx = getStepIndex(status)

  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl shadow-md space-y-4">
      <div className="flex justify-between items-center">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Scan Pipeline Status</h4>
        <span className="text-[10px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded">
          {status}
        </span>
      </div>

      {/* Stepper container */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pt-2">
        {steps.map((step, idx) => {
          const isDone = currentIdx > idx
          const isCurrent = currentIdx === idx
          const isPending = currentIdx < idx

          let circleColor = 'border-slate-800 text-slate-500 bg-slate-900'
          if (isDone) {
            circleColor = 'bg-emerald-500 border-emerald-500 text-slate-900'
          } else if (isCurrent) {
            circleColor = 'border-brand-500 text-brand-400 bg-[#0e1422] shadow shadow-brand-500/20 animate-pulse'
          }

          return (
            <div key={step.key} className="flex-1 flex items-start md:items-center gap-3">
              {/* Checkmark or number indicator */}
              <span className={`w-6 h-6 rounded-full border flex items-center justify-center text-xs font-bold ${circleColor} transition-all duration-300`}>
                {isDone ? (
                  <svg className="w-3.5 h-3.5 stroke-[2.5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  idx + 1
                )}
              </span>
              
              <div className="space-y-0.5 min-w-0">
                <span className={`block text-xs font-bold uppercase tracking-wide ${isCurrent ? 'text-brand-300' : isDone ? 'text-slate-300' : 'text-slate-500'}`}>
                  {step.label}
                </span>
                <span className="block text-[10px] text-slate-500 truncate leading-none">
                  {step.desc}
                </span>
              </div>

              {idx < steps.length - 1 && (
                <div className="hidden md:block flex-1 h-0.5 bg-slate-850 mx-2" />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
