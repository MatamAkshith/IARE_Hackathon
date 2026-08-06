import React from 'react'
import { threatIntelligenceData } from '../data/threatIntelligenceData'
import ThreatFeedPanel from '../components/reports/ThreatFeedPanel'
import IOCTable from '../components/reports/IOCTable'
import ReputationCard from '../components/reports/ReputationCard'
import RecommendationsPanel from '../components/reports/RecommendationsPanel'
import IncidentReportPreview from '../components/reports/IncidentReportPreview'
import ExportPreview from '../components/reports/ExportPreview'

export default function Reports() {
  const { threatFeeds, iocs, reputation, recommendations, reportPreview, exportOptions } = threatIntelligenceData

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Threat Intelligence & Reports</h1>
        <p className="text-xs text-slate-400">
          Analyze reputation scores from third-party intel databases, track IOC tags, and preview formatted incident reports.
        </p>
      </div>

      {/* Grid panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left Side: Feeds list, IOC logs table, and Incident report page sheet */}
        <div className="lg:col-span-2 space-y-6">
          <ThreatFeedPanel feeds={threatFeeds} />
          
          <IOCTable iocs={iocs} />
          
          <IncidentReportPreview report={reportPreview} />
        </div>

        {/* Right Side: Verdict Dial, Recommendations checklist, and Export Previews */}
        <div className="space-y-6">
          <ReputationCard reputation={reputation} />
          
          <RecommendationsPanel recommendations={recommendations} />
          
          <ExportPreview options={exportOptions} />
        </div>
      </div>
    </div>
  )
}
