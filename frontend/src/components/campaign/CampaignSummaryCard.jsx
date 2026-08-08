import React from 'react'

/**
 * Campaign Summary dashboard panel.
 * 
 * @param {Object} props
 * @param {Object} props.summary Campaign summary details from dataset
 */
import { getSeverityDetails } from '../../utils/severityUtils'

export default function CampaignSummaryCard({ summary = {} }) {
  const details = getSeverityDetails(summary.riskLevel || 'HIGH')
  
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl shadow-md space-y-4">
      {/* Title bar */}
      <div className="flex justify-between items-start gap-4 border-b border-[#1a2336]/60 pb-3.5">
        <div className="space-y-1">
          <span className="block text-[9px] uppercase font-extrabold tracking-widest text-brand-400">
            Attributed Campaign Cluster
          </span>
          <h2 className="text-lg font-black text-slate-100">{summary.campaignName}</h2>
          <span className="inline-block text-[10px] font-mono font-bold text-slate-400 bg-slate-800/40 px-2 py-0.5 border border-slate-700/50 rounded">
            ID: {summary.campaignId}
          </span>
        </div>

        <div className="flex flex-col items-end gap-1 flex-shrink-0">
          <span className="text-[10px] font-mono font-bold uppercase text-emerald-400 bg-emerald-950/20 px-2.5 py-0.5 border border-emerald-850/30 rounded flex items-center gap-1.5 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            {summary.status}
          </span>
          <span className={`text-[10px] font-mono font-bold uppercase border px-2 py-0.5 rounded mt-1 ${details.badgeClass}`}>
            {summary.riskLevel}
          </span>
        </div>
      </div>


      {/* Grid details */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
        <div className="p-3 bg-[#0d1322]/55 border border-[#141d2e] rounded-lg">
          <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">First Ingestion</span>
          <span className="font-semibold text-slate-200 block mt-0.5 truncate font-mono">{summary.firstSeen}</span>
        </div>
        <div className="p-3 bg-[#0d1322]/55 border border-[#141d2e] rounded-lg">
          <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Latest Activity</span>
          <span className="font-semibold text-slate-200 block mt-0.5 truncate font-mono">{summary.lastSeen}</span>
        </div>
        <div className="p-3 bg-[#0d1322]/55 border border-[#141d2e] rounded-lg">
          <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Active Domains</span>
          <span className="font-black text-slate-100 block mt-0.5 font-mono text-sm">
            {summary.activeDomains} / {summary.totalDomains}
          </span>
        </div>
        <div className="p-3 bg-[#0d1322]/55 border border-[#141d2e] rounded-lg">
          <span className="block text-[9px] uppercase font-bold text-slate-500 tracking-wider">Infrastructure Nodes</span>
          <span className="font-black text-slate-100 block mt-0.5 font-mono text-sm">
            {summary.infrastructureCount} Nodes
          </span>
        </div>
      </div>
    </div>
  )
}
