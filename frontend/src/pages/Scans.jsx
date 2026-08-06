import React from 'react'

export default function Scans() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Domain Scanning Queue</h1>
      <p className="text-sm text-slate-400">
        Review suspended domain scans, initiate feature extractions, and investigate detailed WHOIS/DNS/SSL telemetry.
      </p>

      {/* Visual placeholder box */}
      <div className="border border-dashed border-[#1a2336] rounded-xl p-8 bg-[#090d16]/30 text-center text-slate-500 text-xs">
        Active scan telemetry queue list and scan submissions form coming soon.
      </div>
    </div>
  )
}
