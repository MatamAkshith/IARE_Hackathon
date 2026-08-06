import React from 'react'

/**
 * Threat Intelligence feeds summary panel.
 * Houses sub-cards detailing VirusTotal, PhishTank, URLHaus, and AbuseIPDB.
 * 
 * @param {Object} props
 * @param {Object} props.feeds Sub-objects mapping threat indicators
 */
export default function ThreatFeedPanel({ feeds = {} }) {
  const { virusTotal = {}, phishTank = {}, urlHaus = {}, abuseIPDB = {} } = feeds

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide font-sans">External Intelligence Feeds</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* VirusTotal Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-4.5 rounded-xl space-y-3.5 hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between">
          <div className="space-y-1.5">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide">VirusTotal Intel</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded">
                {virusTotal.status}
              </span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Detection Ratio</span>
                <span className="text-rose-400 font-mono font-bold">{virusTotal.detectionRatio}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Reputation Metric</span>
                <span className="text-rose-400 font-mono font-semibold">{virusTotal.reputation}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Community Verdict</span>
                <span className="text-rose-400 font-mono font-semibold">{virusTotal.communityScore}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Threat Ingest Time</span>
                <span className="text-slate-300 font-mono">{virusTotal.lastAnalysis}</span>
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-[#151d2c] flex justify-between items-center text-[10px]">
            <span className="text-slate-500 font-bold uppercase tracking-wider">Severity Verdict</span>
            <span className="px-2 py-0.5 rounded font-mono font-bold uppercase bg-rose-950/20 text-rose-400 border border-rose-850/30">
              {virusTotal.riskLevel}
            </span>
          </div>
        </div>

        {/* PhishTank Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-4.5 rounded-xl space-y-3.5 hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between">
          <div className="space-y-1.5">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide">PhishTank Ingestion</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded">
                {phishTank.status}
              </span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Verdict Status</span>
                <span className="text-rose-400 font-bold font-sans">{phishTank.verifiedStatus}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Reports Ingested</span>
                <span className="text-slate-300 font-mono font-bold">{phishTank.phishingReports} logs</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Impersonation Target</span>
                <span className="text-slate-300 font-semibold">{phishTank.targetBrand}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Submission Date</span>
                <span className="text-slate-400 font-mono">{phishTank.submissionDate}</span>
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-[#151d2c] flex justify-between items-center text-[10px]">
            <span className="text-slate-500 font-bold uppercase tracking-wider">Scoring Confidence</span>
            <span className="px-2 py-0.5 rounded font-mono font-bold uppercase bg-brand-950/20 text-brand-400 border border-brand-850/30">
              {phishTank.confidence}
            </span>
          </div>
        </div>

        {/* URLHaus Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-4.5 rounded-xl space-y-3.5 hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between">
          <div className="space-y-1.5">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide">URLHaus Database</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded">
                {urlHaus.status}
              </span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Malware Family</span>
                <span className="text-slate-300 font-semibold">{urlHaus.malwareFamily}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Threat Category</span>
                <span className="text-rose-400 font-mono font-bold">{urlHaus.threatCategory}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Domain Status</span>
                <span className="text-rose-400 font-bold font-sans">{urlHaus.urlStatus}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Active Host Status</span>
                <span className="text-rose-400 font-mono font-bold">{urlHaus.hostStatus}</span>
              </div>
            </div>
          </div>
          <div className="pt-2.5 border-t border-[#151d2c] flex flex-wrap gap-1">
            {urlHaus.tags?.map((tag, idx) => (
              <span key={idx} className="px-1.5 py-0.5 rounded text-[8.5px] font-mono font-bold bg-[#141b2c] text-slate-400 border border-slate-800">
                #{tag}
              </span>
            ))}
          </div>
        </div>

        {/* AbuseIPDB Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-4.5 rounded-xl space-y-3.5 hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between">
          <div className="space-y-1.5">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide">AbuseIPDB Registry</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded">
                {abuseIPDB.status}
              </span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Geo IP Country</span>
                <span className="text-slate-300 font-medium font-sans">{abuseIPDB.country}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Hosting ISP Provider</span>
                <span className="text-slate-300 font-mono truncate max-w-[150px]">{abuseIPDB.isp}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Target Type</span>
                <span className="text-slate-400">{abuseIPDB.usageType}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-slate-500">Total Abuse Reports</span>
                <span className="text-rose-400 font-mono font-bold">{abuseIPDB.reports} cases</span>
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-[#151d2c] flex justify-between items-center text-[10px]">
            <span className="text-slate-500 font-bold uppercase tracking-wider">Abuse Confidence</span>
            <span className="px-2 py-0.5 rounded font-mono font-bold uppercase bg-rose-950/20 text-rose-400 border border-rose-850/30 animate-pulse">
              {abuseIPDB.abuseConfidence}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
