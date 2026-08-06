import React from 'react'

export default function Reports() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Security Incident Reporting</h1>
      <p className="text-sm text-slate-400">
        Generate and export detailed incident reports in Markdown or PDF formats for executive handoffs and domain registrar take-down requests.
      </p>

      {/* Visual placeholder box */}
      <div className="border border-dashed border-[#1a2336] rounded-xl p-8 bg-[#090d16]/30 text-center text-slate-500 text-xs">
        Report generators, draft take-down notices, and exporter controls coming soon.
      </div>
    </div>
  )
}
