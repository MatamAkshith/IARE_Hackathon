import React from 'react'

/**
 * Report Export shortcuts panel.
 * 
 * @param {Object} props
 * @param {Array} props.options Export formats options list
 * @param {Object} props.report The current Incident Report Preview data
 */
export default function ExportPreview({ options = [], report = {} }) {
  const handleExport = (formatId) => {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC'
    let filename = 'incident-report'
    let content = ''
    let mimeType = 'text/plain'

    if (formatId === 'MD') {
      filename = `${filename}.md`
      mimeType = 'text/markdown'
      content = `# CONFIDENTIAL SOC THREAT INTEL REPORT: ${report.title || 'ThreatLens Report'}\n` +
        `**GENERATE TIMESTAMP**: ${timestamp}\n\n` +
        `### Executive Threat Summary\n${report.executiveSummary || 'N/A'}\n\n` +
        `### Technical Vector Description\n${report.threatDescription || 'N/A'}\n\n` +
        `### Scoring & Risk Assessment\n${report.riskAssessment || 'N/A'}\n\n` +
        `### Operational Impact Sizing\n${report.impact || 'N/A'}\n\n` +
        `### Chronological Timeline Summary\n${report.timelineSummary || 'N/A'}\n\n` +
        `### Indicators Counts Summary\n${report.indicatorsSummary || 'N/A'}\n\n` +
        `### Attribution & Analyst Notes\n${report.analystNotes || 'N/A'}\n\n` +
        `### Mitigation Checklist Actions\n${report.recommendations || 'N/A'}\n`
    } else if (formatId === 'JSON') {
      filename = `${filename}.json`
      mimeType = 'application/json'
      content = JSON.stringify({
        title: report.title || 'ThreatLens Report',
        generate_timestamp: timestamp,
        sections: {
          executiveSummary: report.executiveSummary || '',
          threatDescription: report.threatDescription || '',
          riskAssessment: report.riskAssessment || '',
          impact: report.impact || '',
          timelineSummary: report.timelineSummary || '',
          indicatorsSummary: report.indicatorsSummary || '',
          analystNotes: report.analystNotes || '',
          recommendations: report.recommendations || ''
        }
      }, null, 2)
    } else {
      return
    }

    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4 shadow-md w-full min-w-0 overflow-hidden">
      <div className="flex items-center justify-between border-b border-[#1a2336]/60 pb-3 gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <svg className="w-5 h-5 text-brand-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <h3 className="font-semibold text-slate-200 text-sm tracking-wide truncate">Export Incident Formats</h3>
        </div>
        <span className="text-[8px] font-mono font-bold uppercase text-emerald-400 bg-emerald-950/20 px-2 py-0.5 border border-emerald-850/30 rounded flex-shrink-0">
          Live Export Enabled
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {options.map((opt) => (
          <button
            key={opt.id}
            type="button"
            onClick={() => handleExport(opt.id)}
            className="p-3 bg-[#0d1322]/55 border border-[#141d2e] rounded-lg text-left space-y-1 hover:border-brand-500 hover:bg-[#0f192b] transition-all cursor-pointer group"
            title={`Download ${opt.name}`}
          >
            <div className="flex justify-between items-center gap-1.5 min-w-0">
              <span className="block text-[10px] font-bold text-slate-350 uppercase tracking-wide truncate group-hover:text-brand-400">
                {opt.name}
              </span>
              <svg className="w-3.5 h-3.5 text-slate-500 flex-shrink-0 group-hover:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
            <span className="block text-[9px] text-slate-500 leading-tight">
              {opt.desc}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
