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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full min-w-0">
        {/* VirusTotal Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full h-full min-w-0 overflow-hidden">
          <div className="space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2.5 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">VirusTotal Intel</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2.5 py-1 border border-brand-850/30 rounded flex-shrink-0 h-5.5 flex items-center justify-center">
                {virusTotal.status}
              </span>
            </div>
            <div className="text-xs w-full min-w-0">
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Detection Ratio</span>
                <span className="text-rose-400 font-mono font-bold text-right break-words min-w-0 flex-1 text-xs">{virusTotal.detectionRatio}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Reputation Metric</span>
                <span className="text-rose-400 font-mono font-semibold text-right break-words min-w-0 flex-1 text-xs">{virusTotal.reputation}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Community Verdict</span>
                <span className="text-rose-400 font-mono font-semibold text-right break-words min-w-0 flex-1 text-xs">{virusTotal.communityScore}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Ingest Time</span>
                <span className="text-slate-300 font-mono text-right break-words min-w-0 flex-1 text-xs">{virusTotal.lastAnalysis}</span>
              </div>
            </div>
          </div>
          <div className="pt-4 mt-4 border-t border-[#1a2336]/60 flex justify-between items-center text-[10.5px] min-w-0">
            <span className="text-slate-500 font-bold uppercase tracking-widest text-[9.5px] truncate">Severity Verdict</span>
            <span className="px-2.5 py-1 rounded font-mono font-bold uppercase bg-rose-950/20 text-rose-400 border border-rose-850/30 flex-shrink-0 h-5.5 flex items-center justify-center">
              {virusTotal.riskLevel}
            </span>
          </div>
        </div>

        {/* PhishTank Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full h-full min-w-0 overflow-hidden">
          <div className="space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2.5 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">PhishTank Ingestion</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2.5 py-1 border border-brand-850/30 rounded flex-shrink-0 h-5.5 flex items-center justify-center">
                {phishTank.status}
              </span>
            </div>
            <div className="text-xs w-full min-w-0">
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Verdict Status</span>
                <span className="text-rose-400 font-bold font-sans text-right break-words min-w-0 flex-1 text-xs">{phishTank.verifiedStatus}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Reports Ingested</span>
                <span className="text-slate-300 font-mono font-bold text-right break-words min-w-0 flex-1 text-xs">{phishTank.phishingReports} logs</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Target Brand</span>
                <span className="text-slate-300 font-semibold text-right break-words min-w-0 flex-1 text-xs">{phishTank.targetBrand}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Submission Date</span>
                <span className="text-slate-400 font-mono text-right break-words min-w-0 flex-1 text-xs">{phishTank.submissionDate}</span>
              </div>
            </div>
          </div>
          <div className="pt-4 mt-4 border-t border-[#1a2336]/60 flex justify-between items-center text-[10.5px] min-w-0">
            <span className="text-slate-500 font-bold uppercase tracking-widest text-[9.5px] truncate">Scoring Confidence</span>
            <span className="px-2.5 py-1 rounded font-mono font-bold uppercase bg-brand-950/20 text-brand-400 border border-brand-850/30 flex-shrink-0 h-5.5 flex items-center justify-center">
              {phishTank.confidence}
            </span>
          </div>
        </div>

        {/* URLHaus Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full h-full min-w-0 overflow-hidden">
          <div className="space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2.5 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">URLHaus Database</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2.5 py-1 border border-brand-850/30 rounded flex-shrink-0 h-5.5 flex items-center justify-center">
                {urlHaus.status}
              </span>
            </div>
            <div className="text-xs w-full min-w-0">
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Malware Family</span>
                <span className="text-slate-300 font-semibold text-right break-words min-w-0 flex-1 text-xs">{urlHaus.malwareFamily}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Threat Category</span>
                <span className="text-rose-400 font-mono font-bold text-right break-words min-w-0 flex-1 text-xs">{urlHaus.threatCategory}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Domain Status</span>
                <span className="text-rose-400 font-bold font-sans text-right break-words min-w-0 flex-1 text-xs">{urlHaus.urlStatus}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Host Status</span>
                <span className="text-rose-400 font-mono font-bold text-right break-words min-w-0 flex-1 text-xs">{urlHaus.hostStatus}</span>
              </div>
            </div>
          </div>
          <div className="pt-4 mt-4 border-t border-[#1a2336]/60 flex justify-between items-center text-[10.5px] min-w-0">
            <span className="text-slate-500 font-bold uppercase tracking-widest text-[9.5px] truncate">Attribution Tags</span>
            <div className="flex flex-wrap gap-1 justify-end max-w-[62%]">
              {urlHaus.tags?.map((tag, idx) => (
                <span key={idx} className="px-1.5 py-0.5 rounded text-[8.5px] font-mono font-bold bg-[#141b2c] text-slate-400 border border-slate-850 flex-shrink-0">
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* AbuseIPDB Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full h-full min-w-0 overflow-hidden">
          <div className="space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2.5 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">AbuseIPDB Registry</span>
              <span className="text-[9px] font-mono font-bold uppercase text-brand-400 bg-brand-950/20 px-2.5 py-1 border border-brand-850/30 rounded flex-shrink-0 h-5.5 flex items-center justify-center">
                {abuseIPDB.status}
              </span>
            </div>
            <div className="text-xs w-full min-w-0">
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Geo IP Country</span>
                <span className="text-slate-300 font-medium font-sans text-right break-words min-w-0 flex-1 text-xs">{abuseIPDB.country}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Hosting ISP</span>
                <span className="text-slate-300 font-mono text-right break-words min-w-0 flex-1 text-xs">{abuseIPDB.isp}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Usage Type</span>
                <span className="text-slate-400 text-right break-words min-w-0 flex-1 text-xs">{abuseIPDB.usageType}</span>
              </div>
              <div className="flex justify-between items-start py-2.5 border-b border-[#151d2c]/50 last:border-b-0 gap-3 w-full min-w-0">
                <span className="text-slate-500 w-[38%] flex-shrink-0 text-left truncate font-bold text-[9px] uppercase tracking-wider">Total Reports</span>
                <span className="text-rose-400 font-mono font-bold text-right break-words min-w-0 flex-1 text-xs">{abuseIPDB.reports} cases</span>
              </div>
            </div>
          </div>
          <div className="pt-4 mt-4 border-t border-[#1a2336]/60 flex justify-between items-center text-[10.5px] min-w-0">
            <span className="text-slate-500 font-bold uppercase tracking-widest text-[9.5px] truncate">Abuse Confidence</span>
            <span className="px-2.5 py-1 rounded font-mono font-bold uppercase bg-rose-950/20 text-rose-400 border border-rose-850/30 animate-pulse flex-shrink-0 h-5.5 flex items-center justify-center">
              {abuseIPDB.abuseConfidence}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
