import React from 'react'

/**
 * Shared Evidence logs table.
 * 
 * @param {Object} props
 * @param {Array} props.evidence Correlation evidence array from dataset
 */
export default function EvidenceTable({ evidence = [] }) {
  const getSeverityStyle = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'text-rose-400 bg-rose-950/20 border-rose-900/30'
      case 'medium':
        return 'text-amber-400 bg-amber-950/20 border-amber-900/30'
      default:
        return 'text-emerald-400 bg-emerald-950/20 border-emerald-900/30'
    }
  }

  return (
    <div className="border border-[#1a2336] bg-[#090d16] rounded-xl overflow-hidden shadow-md">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[#1a2336] bg-[#0c121e]/80 flex items-center gap-2">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Infrastructure Correlation Parameters</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-[#0b0f19] border-b border-[#1a2336] text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-5">Correlation Param</th>
              <th className="py-3 px-5">Evidence Details</th>
              <th className="py-3 px-5">Severity</th>
              <th className="py-3 px-5 text-right">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {evidence.map((item, idx) => (
              <tr
                key={idx}
                className="border-b border-[#151d2c] last:border-b-0 hover:bg-[#101726]/40 transition-colors"
              >
                <td className="py-3.5 px-5 font-mono text-[11px] font-semibold text-slate-300">
                  {item.type}
                </td>
                <td className="py-3.5 px-5 text-slate-400 font-medium font-sans">
                  {item.description}
                </td>
                <td className="py-3.5 px-5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${getSeverityStyle(item.severity)}`}>
                    {item.severity}
                  </span>
                </td>
                <td className="py-3.5 px-5 text-right font-mono text-slate-300 font-semibold text-[11px]">
                  {item.confidence}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
