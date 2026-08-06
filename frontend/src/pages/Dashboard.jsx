import React from 'react'

export default function Dashboard() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Security Operations Center Dashboard</h1>
      <p className="text-sm text-slate-400">
        Monitor real-time threat intelligence ingestion pipeline, aggregate active campaigns, and track domain risk scoring statistics.
      </p>
      
      {/* Visual placeholder box */}
      <div className="border border-dashed border-[#1a2336] rounded-xl p-8 bg-[#090d16]/30 text-center text-slate-500 text-xs">
        Dashboard telemetry analytics and risk score controls coming soon.
      </div>
    </div>
  )
}
