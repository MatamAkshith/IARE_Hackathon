import React from 'react'

/**
 * Top Threat Highlights panel.
 * 
 * @param {Object} props
 * @param {Object} props.summary Key highlights statistics object
 */
export default function ThreatSummary({ summary = {} }) {
  const summaryItems = [
    { label: 'Most Targeted Enterprise Brand', value: summary.mostTargetedBrand },
    { label: 'Primary Threat Vector Class', value: summary.mostCommonAttack },
    { label: 'Top Suspicious TLD suffix', value: summary.mostCommonTLD },
    { label: 'Highest Scored Domain Threat', value: summary.highestRiskDomain, highlight: true },
    { label: 'Latest pipeline trigger', value: summary.latestScan }
  ]

  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Threat Vectors Intelligence</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <tbody>
            {summaryItems.map((item, idx) => (
              <tr
                key={idx}
                className="border-b border-[#151d2c]/65 last:border-b-0 hover:bg-[#101726]/30 transition-colors"
              >
                <td className="py-2.5 pr-4 font-semibold text-slate-400 font-sans w-1/2">
                  {item.label}
                </td>
                <td
                  className={`py-2.5 font-mono text-[11px] text-right font-medium ${
                    item.highlight ? 'text-rose-400 font-bold' : 'text-slate-300'
                  }`}
                >
                  {item.value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
