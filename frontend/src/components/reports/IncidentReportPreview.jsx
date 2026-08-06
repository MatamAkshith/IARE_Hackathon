import React from 'react'

/**
 * Incident Report Preview card.
 * Renders a structured threat intelligence report draft sheet.
 * 
 * @param {Object} props
 * @param {Object} props.report Incident report summary data from dataset
 */
export default function IncidentReportPreview({ report = {} }) {
  const sections = [
    { label: 'Executive Threat Summary', value: report.executiveSummary },
    { label: 'Technical Vector Description', value: report.threatDescription },
    { label: 'Scoring & Risk Assessment', value: report.riskAssessment, highlight: true },
    { label: 'Operational Impact Sizing', value: report.impact },
    { label: 'Chronological Timeline Summary', value: report.timelineSummary },
    { label: 'Indicators Counts Summary', value: report.indicatorsSummary },
    { label: 'Attribution & Analyst Notes', value: report.analystNotes },
    { label: 'Mitigation Checklist Actions', value: report.recommendations }
  ]

  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl shadow-md space-y-4">
      {/* Title */}
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Incident Report Preview</h3>
      </div>

      {/* Structured report paper container */}
      <div className="bg-[#070a12]/80 border border-[#141c2d] p-5 rounded-lg space-y-5 font-sans select-all leading-relaxed text-xs">
        <div className="border-b border-[#1a2336]/40 pb-3 text-center">
          <span className="text-[10px] font-mono font-bold text-rose-400 uppercase tracking-widest block">
            CONFIDENTIAL SOC THREAT INTEL REPORT
          </span>
          <h2 className="text-sm font-bold text-slate-100 mt-1 font-mono tracking-tight">{report.title}</h2>
          <span className="text-[9px] font-mono text-slate-500 mt-0.5 block">GENERATE TIMESTAMP: 2026-08-07 00:30:00Z</span>
        </div>

        {/* Section categories */}
        <div className="space-y-4 font-sans">
          {sections.map((sec, idx) => (
            <div key={idx} className="space-y-1">
              <span className="block text-[9px] font-mono font-bold text-slate-500 uppercase tracking-wider">
                {sec.label}
              </span>
              <p className={`text-[11px] font-medium leading-relaxed ${
                sec.highlight ? 'text-rose-300 font-semibold' : 'text-slate-300'
              }`}>
                {sec.value}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
