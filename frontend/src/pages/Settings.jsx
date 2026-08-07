import React from 'react'

export default function Settings() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Console Settings & Feeds Configuration</h1>
      <p className="text-sm text-slate-400">
        Manage API credentials for external intelligence databases (e.g. VirusTotal, PhishTank) and configure default scoring weights.
      </p>

      {/* Visual placeholder box */}
      <div className="border border-dashed border-[#1a2336] rounded-xl p-8 bg-[#090d16]/30 text-center text-slate-500 text-xs">
        Threat intelligence API configuration sliders and settings coming soon.
      </div>
    </div>
  )
}
