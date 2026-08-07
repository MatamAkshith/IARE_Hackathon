import React, { useState } from 'react'

/**
 * Collapsible accordion panel displaying evidence categories.
 * 
 * @param {Object} props
 * @param {Object} props.evidence Categories dataset { domain: [], dns: [], etc. }
 */
export default function EvidenceAccordion({ evidence = {} }) {
  // Manage open state for each category
  const [openSections, setOpenSections] = useState({
    domain: true,
    dns: true,
    whois: false,
    ssl: false,
    html: false,
    metadata: false
  })

  const toggleSection = (key) => {
    setOpenSections(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const sections = [
    { key: 'domain', label: 'Domain Metadata' },
    { key: 'dns', label: 'Active DNS Records' },
    { key: 'whois', label: 'WHOIS Registration Telemetry' },
    { key: 'ssl', label: 'SSL/TLS Certificate profile' },
    { key: 'html', label: 'HTML structural metrics' },
    { key: 'metadata', label: 'HTTP response metadata' }
  ]

  return (
    <div className="space-y-3">
      {sections.map((sec) => {
        const isOpen = openSections[sec.key]
        const items = evidence[sec.key] || []

        return (
          <div key={sec.key} className="border border-[#1a2336] bg-[#090d16] rounded-xl overflow-hidden shadow-sm">
            {/* Header toggle block */}
            <button
              type="button"
              onClick={() => toggleSection(sec.key)}
              className="w-full px-5 py-3.5 bg-[#0c121e] border-b border-[#1a2336] hover:bg-[#121927] transition-all flex items-center justify-between text-left"
            >
              <span className="font-semibold text-slate-200 text-xs uppercase tracking-wider">
                {sec.label}
              </span>
              <span className="text-slate-400">
                {isOpen ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" />
                  </svg>
                )}
              </span>
            </button>

            {/* Collapsible details table */}
            {isOpen && (
              <div className="p-5 overflow-x-auto animate-fade-in">
                <table className="w-full text-left text-xs">
                  <tbody>
                    {items.map((item, idx) => (
                      <tr
                        key={idx}
                        className="border-b border-[#151d2c]/65 last:border-b-0 hover:bg-[#0d1322]/40 transition-colors"
                      >
                        <td className="py-2.5 pr-4 font-medium text-slate-400 w-1/3">
                          {item.label}
                        </td>
                        <td
                          className={`py-2.5 font-mono ${
                            item.mono ? 'font-mono text-[11px] text-slate-300' : 'font-sans text-slate-200'
                          } ${item.highlight ? 'text-amber-400 font-semibold' : ''}`}
                        >
                          {item.value}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
