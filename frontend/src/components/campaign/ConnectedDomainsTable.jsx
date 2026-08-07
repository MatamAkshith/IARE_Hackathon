import React from 'react'
import RiskScoreBadge from '../RiskScoreBadge'

/**
 * Connected lookalike domains list table.
 * 
 * @param {Object} props
 * @param {Array} props.domains Connected domains logs list from dataset
 */
export default function ConnectedDomainsTable({ domains = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] rounded-xl overflow-hidden shadow-md">
      {/* Header title */}
      <div className="px-5 py-4 border-b border-[#1a2336] bg-[#0c121e]/80 flex items-center gap-2">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Correlated Campaign Domains</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-[#0b0f19] border-b border-[#1a2336] text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-5">Domain Name</th>
              <th className="py-3 px-5">Risk Rating</th>
              <th className="py-3 px-5">Status</th>
              <th className="py-3 px-5">First Logged</th>
              <th className="py-3 px-5">Latest Logged</th>
              <th className="py-3 px-5">Geo IP Country</th>
              <th className="py-3 px-5 text-right">Hosting Provider</th>
            </tr>
          </thead>
          <tbody>
            {domains.map((dom) => (
              <tr
                key={dom.id}
                className="border-b border-[#151d2c] last:border-b-0 hover:bg-[#101726]/40 transition-colors"
              >
                <td className="py-3.5 px-5 font-mono text-[11px] font-semibold text-slate-300 select-all truncate max-w-[200px]" title={dom.domain}>
                  {dom.domain}
                </td>
                <td className="py-3.5 px-5">
                  <RiskScoreBadge score={dom.riskScore} />
                </td>
                <td className="py-3.5 px-5">
                  <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider bg-emerald-950/20 text-emerald-400 border-emerald-900/30">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    {dom.status}
                  </span>
                </td>
                <td className="py-3.5 px-5 font-mono text-slate-400 text-[10px]">
                  {dom.firstSeen}
                </td>
                <td className="py-3.5 px-5 font-mono text-slate-400 text-[10px]">
                  {dom.lastSeen}
                </td>
                <td className="py-3.5 px-5 text-slate-400 font-medium font-sans">
                  {dom.country}
                </td>
                <td className="py-3.5 px-5 text-right font-mono text-slate-400 text-[11px] font-semibold">
                  {dom.hostingProvider}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
