import React from 'react'
import { getSeverityDetails } from '../../utils/severityUtils'

/**
 * Indicators of Compromise (IOC) telemetry table.
 * 
 * @param {Object} props
 * @param {Array} props.iocs List of IOC entries
 */
export default function IOCTable({ iocs = [] }) {
  const getSeverityStyle = (severity) => {
    return getSeverityDetails(severity).badgeClass
  }

  return (
    <div className="border border-[#1a2336] bg-[#090d16] rounded-xl overflow-hidden shadow-md">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[#1a2336] bg-[#0c121e]/80 flex items-center gap-2">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7 a 2 2 0 0 0 -2 2 v12 a 2 2 0 0 0 2 2 h10 a 2 2 0 0 0 2 -2 V7 a 2 2 0 0 0 -2 -2 h-2 M9 5 a 2 2 0 0 0 2 2 h2 a 2 2 0 0 0 2 -2 M9 5 a 2 2 0 0 1 2 -2 h2 a 2 2 0 0 1 2 2" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide font-sans">Indicators of Compromise (IOCs)</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-[#0b0f19] border-b border-[#1a2336] text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-5">IOC Type</th>
              <th className="py-3 px-5">Value</th>
              <th className="py-3 px-5">Verification Feed</th>
              <th className="py-3 px-5">Severity</th>
              <th className="py-3 px-5">Confidence</th>
              <th className="py-3 px-5 text-right">Status</th>
            </tr>
          </thead>
          <tbody>
            {iocs.map((ioc, idx) => (
              <tr
                key={idx}
                className="border-b border-[#151d2c] last:border-b-0 hover:bg-[#101726]/40 transition-colors"
              >
                <td className="py-3.5 px-5 font-sans font-bold text-slate-400 uppercase text-[10px]">
                  {ioc.type}
                </td>
                <td className="py-3.5 px-5 font-mono text-[11px] font-semibold text-slate-300 select-all truncate max-w-[200px]" title={ioc.value}>
                  {ioc.value}
                </td>
                <td className="py-3.5 px-5 font-sans text-slate-400 font-semibold">
                  {ioc.source}
                </td>
                <td className="py-3.5 px-5">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold uppercase border ${getSeverityStyle(ioc.severity)}`}>
                    {ioc.severity}
                  </span>
                </td>
                <td className="py-3.5 px-5 font-mono text-slate-300 font-semibold text-[11px]">
                  {ioc.confidence}
                </td>
                <td className="py-3.5 px-5 text-right font-sans text-slate-500 text-[10px] font-bold uppercase tracking-wider">
                  {ioc.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
