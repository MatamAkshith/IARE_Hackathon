import React from 'react'

/**
 * Shared Campaign Infrastructure block panel.
 * 
 * @param {Object} props
 * @param {Object} props.infrastructure Shared infrastructure keys from dataset
 */
export default function InfrastructureCard({ infrastructure = {} }) {
  const items = [
    { label: 'Shared Ingestion IP', value: infrastructure.ipAddress, mono: true, highlight: true },
    { label: 'Autonomous System Number (ASN)', value: infrastructure.asn, mono: true },
    { label: 'Hosting Authority', value: infrastructure.hostingProvider },
    { label: 'Domain Registrar Authority', value: infrastructure.registrar },
    { label: 'Authority Nameservers', value: infrastructure.nameservers, mono: true },
    { label: 'Common SSL SHA-256 Fingerprint', value: infrastructure.sslFingerprint, mono: true, wrap: true },
    { label: 'WHOIS Relational Similarity', value: infrastructure.whoisSimilarity, highlight: true }
  ]

  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4 shadow-md w-full min-w-0 overflow-hidden">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Shared Threat Infrastructure</h3>
      </div>

      <div className="space-y-3.5">
        {items.map((item, idx) => (
          <div key={idx} className="flex flex-col sm:flex-row sm:justify-between sm:items-start border-b border-[#151d2c]/65 last:border-b-0 pb-2.5 last:pb-0 gap-1.5 w-full min-w-0">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex-shrink-0">
              {item.label}
            </span>
            <span
              className={`text-xs ${
                item.mono ? 'font-mono text-[11px]' : 'font-sans'
              } ${item.highlight ? 'text-amber-400 font-semibold' : 'text-slate-300'} ${
                item.wrap ? 'break-all leading-normal text-right max-w-md' : 'text-right'
              }`}
            >
              {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
