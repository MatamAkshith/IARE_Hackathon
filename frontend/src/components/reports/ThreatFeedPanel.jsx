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
    <div className="space-y-6 w-full min-w-0">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3 min-w-0">
        <svg className="w-5 h-5 text-brand-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide font-sans truncate">External Intelligence Feeds</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full min-w-0">
        {/* VirusTotal Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-4.5 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full min-w-0 overflow-hidden">
          <div className="space-y-3.5 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">VirusTotal Intel</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded flex-shrink-0">
                {virusTotal.status}
              </span>
            </div>
            <div className="text-xs w-full min-w-0">
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Detection Ratio</span>
                <span className="text-rose-400 font-mono font-bold text-right break-words min-w-0 flex-1">{virusTotal.detectionRatio}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Reputation Metric</span>
                <span className="text-rose-400 font-mono font-semibold text-right break-words min-w-0 flex-1">{virusTotal.reputation}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Community Verdict</span>
                <span className="text-rose-400 font-mono font-semibold text-right break-words min-w-0 flex-1">{virusTotal.communityScore}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Threat Ingest Time</span>
                <span className="text-slate-300 font-mono text-right break-words min-w-0 flex-1">{virusTotal.lastAnalysis}</span>
              </div>
            </div>
          </div>
          <div className="pt-2.5 mt-3.5 border-t border-[#151d2c] flex justify-between items-center text-[10px] min-w-0">
            <span className="text-slate-500 font-bold uppercase tracking-wider truncate">Severity Verdict</span>
            <span className="px-2 py-0.5 rounded font-mono font-bold uppercase bg-rose-950/20 text-rose-400 border border-rose-850/30 flex-shrink-0">
              {virusTotal.riskLevel}
            </span>
          </div>
        </div>

        {/* PhishTank Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-4.5 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full min-w-0 overflow-hidden">
          <div className="space-y-3.5 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">PhishTank Ingestion</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded flex-shrink-0">
                {phishTank.status}
              </span>
            </div>
            <div className="text-xs w-full min-w-0">
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Verdict Status</span>
                <span className="text-rose-400 font-bold font-sans text-right break-words min-w-0 flex-1">{phishTank.verifiedStatus}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Reports Ingested</span>
                <span className="text-slate-300 font-mono font-bold text-right break-words min-w-0 flex-1">{phishTank.phishingReports} logs</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Impersonation Target</span>
                <span className="text-slate-300 font-semibold text-right break-words min-w-0 flex-1">{phishTank.targetBrand}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Submission Date</span>
                <span className="text-slate-400 font-mono text-right break-words min-w-0 flex-1">{phishTank.submissionDate}</span>
              </div>
            </div>
          </div>
          <div className="pt-2.5 mt-3.5 border-t border-[#151d2c] flex justify-between items-center text-[10px] min-w-0">
            <span className="text-slate-500 font-bold uppercase tracking-wider truncate">Scoring Confidence</span>
            <span className="px-2 py-0.5 rounded font-mono font-bold uppercase bg-brand-950/20 text-brand-400 border border-brand-850/30 flex-shrink-0">
              {phishTank.confidence}
            </span>
          </div>
        </div>

        {/* URLHaus Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-4.5 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full min-w-0 overflow-hidden">
          <div className="space-y-3.5 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">URLHaus Database</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded flex-shrink-0">
                {urlHaus.status}
              </span>
            </div>
            <div className="text-xs w-full min-w-0">
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Malware Family</span>
                <span className="text-slate-300 font-semibold text-right break-words min-w-0 flex-1">{urlHaus.malwareFamily}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Threat Category</span>
                <span className="text-rose-400 font-mono font-bold text-right break-words min-w-0 flex-1">{urlHaus.threatCategory}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Domain Status</span>
                <span className="text-rose-400 font-bold font-sans text-right break-words min-w-0 flex-1">{urlHaus.urlStatus}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Active Host Status</span>
                <span className="text-rose-400 font-mono font-bold text-right break-words min-w-0 flex-1">{urlHaus.hostStatus}</span>
              </div>
            </div>
          </div>
          <div className="pt-2.5 mt-3.5 border-t border-[#151d2c] flex flex-wrap gap-1 min-w-0">
            {urlHaus.tags?.map((tag, idx) => (
              <span key={idx} className="px-1.5 py-0.5 rounded text-[8.5px] font-mono font-bold bg-[#141b2c] text-slate-400 border border-slate-800 flex-shrink-0">
                #{tag}
              </span>
            ))}
          </div>
        </div>

        {/* AbuseIPDB Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-4.5 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full min-w-0 overflow-hidden">
          <div className="space-y-3.5 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">AbuseIPDB Registry</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2 py-0.5 border border-brand-850/30 rounded flex-shrink-0">
                {abuseIPDB.status}
              </span>
            </div>
            <div className="text-xs w-full min-w-0">
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Geo IP Country</span>
                <span className="text-slate-300 font-medium font-sans text-right break-words min-w-0 flex-1">{abuseIPDB.country}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Hosting ISP Provider</span>
                <span className="text-slate-300 font-mono text-right break-words min-w-0 flex-1">{abuseIPDB.isp}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Usage Type</span>
                <span className="text-slate-400 text-right break-words min-w-0 flex-1">{abuseIPDB.usageType}</span>
              </div>
              <div className="flex justify-between items-start py-1.5 border-b border-[#151d2c]/50 last:border-b-0 gap-2.5 w-full min-w-0">
                <span className="text-slate-500 w-36 flex-shrink-0 text-left truncate font-medium">Total Abuse Reports</span>
                <span className="text-rose-400 font-mono font-bold text-right break-words min-w-0 flex-1">{abuseIPDB.reports} cases</span>
              </div>
            </div>
          </div>
          <div className="pt-2.5 mt-3.5 border-t border-[#151d2c] flex justify-between items-center text-[10px] min-w-0">
            <span className="text-slate-500 font-bold uppercase tracking-wider truncate">Abuse Confidence</span>
            <span className="px-2 py-0.5 rounded font-mono font-bold uppercase bg-rose-950/20 text-rose-400 border border-rose-850/30 animate-pulse flex-shrink-0">
              {abuseIPDB.abuseConfidence}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
