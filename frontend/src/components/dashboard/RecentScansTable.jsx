import React from 'react'
import { useNavigate } from 'react-router-dom'
import RiskScoreBadge from '../RiskScoreBadge'
import StatusPill from '../StatusPill'

/**
 * Recent Domain scans log list component with row deep-linking.
 * 
 * @param {Object} props
 * @param {Array} props.scans Domain threat scans list from dataset
 */
export default function RecentScansTable({ scans = [] }) {
  const navigate = useNavigate()

  return (
    <div className="border border-[#1a2336] bg-[#090d16] rounded-xl overflow-hidden shadow-md">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[#1a2336] bg-[#0c121e]/80 flex items-center gap-2">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7 a 2 2 0 0 0 -2 2 v12 a 2 2 0 0 0 2 2 h10 a 2 2 0 0 0 2 -2 V7 a 2 2 0 0 0 -2 -2 h-2 M9 5 a 2 2 0 0 0 2 2 h2 a 2 2 0 0 0 2 -2 M9 5 a 2 2 0 0 1 2 -2 h2 a 2 2 0 0 1 2 2" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Threat Monitoring Feed</h3>
      </div>

      {/* Grid container */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-[#0b0f19] border-b border-[#1a2336] text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-5">Target Domain</th>
              <th className="py-3 px-5">Risk Rating</th>
              <th className="py-3 px-5">Pipeline Status</th>
              <th className="py-3 px-5">Campaign Attribution</th>
              <th className="py-3 px-5 text-right">Date/Time</th>
            </tr>
          </thead>
          <tbody>
            {scans.length > 0 ? (
              scans.map((scan) => (
                <tr
                  key={scan.id}
                  onClick={() => navigate(`/scans/${scan.id}`)}
                  className="border-b border-[#151d2c] last:border-b-0 hover:bg-[#101726]/60 transition-colors cursor-pointer"
                  title="Click to view detailed investigation workspace"
                >
                  <td className="py-3.5 px-5 font-mono text-[11px] font-semibold text-slate-300 select-all truncate max-w-[200px]" title={scan.domain}>
                    {scan.domain}
                  </td>
                  <td className="py-3.5 px-5">
                    <RiskScoreBadge score={scan.riskScore} />
                  </td>
                  <td className="py-3.5 px-5">
                    <StatusPill status={scan.status} />
                  </td>
                  <td className="py-3.5 px-5">
                    {scan.campaign !== 'Unattributed' && scan.campaign !== 'Uncorrelated / Individual Threat' ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-brand-900/35 text-brand-300 border border-brand-800/40">
                        {scan.campaign}
                      </span>
                    ) : (
                      <span className="text-slate-500 font-mono text-[10px] italic">Unattributed</span>
                    )}
                  </td>
                  <td className="py-3.5 px-5 text-right font-mono text-slate-500 text-[10px]">
                    {scan.scanTime}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" className="py-6 text-center text-slate-500 font-medium">
                  No scan logs present.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
