import React from 'react'

function getStatusBadgeClass(status) {
  const base = "text-[9px] font-mono font-bold uppercase px-2.5 py-1 border rounded flex-shrink-0 h-5.5 flex items-center justify-center"
  if (status === 'success' || status === 'Active') {
    return `${base} text-emerald-400 bg-emerald-950/20 border-emerald-850/30`
  }
  if (status === 'rate_limited') {
    return `${base} text-amber-400 bg-amber-950/20 border-amber-850/30`
  }
  if (status === 'no_result') {
    return `${base} text-slate-400 bg-slate-950/20 border-slate-850/30`
  }
  return `${base} text-rose-400 bg-rose-950/20 border-rose-850/30`
}

function getStatusBadgeLabel(status) {
  if (status === 'success' || status === 'Active') return 'Success'
  if (status === 'rate_limited') return 'Rate Limited'
  if (status === 'no_result') return 'No Result'
  return 'Unavailable'
}

function renderFeedCardContent(feed, renderSuccess) {
  if (feed.status === 'rate_limited') {
    return (
      <div className="flex flex-col items-center justify-center text-center p-4 py-8 space-y-2 min-h-[160px]">
        <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h4 className="text-amber-400 font-semibold text-xs uppercase tracking-wider">Rate Limited (429)</h4>
        <p className="text-[11px] text-slate-400 max-w-[200px]">
          {feed.error || "Query limit reached. Please wait or check your subscription key."}
        </p>
      </div>
    )
  }
  if (feed.status === 'unavailable') {
    return (
      <div className="flex flex-col items-center justify-center text-center p-4 py-8 space-y-2 min-h-[160px]">
        <svg className="w-8 h-8 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h4 className="text-rose-400 font-semibold text-xs uppercase tracking-wider">Feed Unavailable</h4>
        <p className="text-[11px] text-slate-400 max-w-[200px] break-words">
          {feed.error || "API service is offline or credentials are not configured."}
        </p>
      </div>
    )
  }
  if (feed.status === 'no_result') {
    return (
      <div className="flex flex-col items-center justify-center text-center p-4 py-8 space-y-2 min-h-[160px]">
        <svg className="w-8 h-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h4 className="text-slate-400 font-semibold text-xs uppercase tracking-wider">No Data Found</h4>
        <p className="text-[11px] text-slate-500 max-w-[200px]">
          No recorded security threats found for this indicator.
        </p>
      </div>
    )
  }

  return renderSuccess()
}

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
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172 a 4 4 0 0 0 -5.656 0 l -4 4 a 4 4 0 1 0 5.656 5.656 l 1.102 -1.101 m -0.758 -4.899 a 4 4 0 0 0 5.656 0 l 4 -4 a 4 4 0 0 0 -5.656 -5.656 l -1.1 1.1" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide font-sans truncate">External Intelligence Feeds</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full min-w-0">
        {/* VirusTotal Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full h-full min-w-0 overflow-hidden">
          <div className="space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2.5 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">VirusTotal Intel</span>
              <span className={getStatusBadgeClass(virusTotal.status)}>
                {getStatusBadgeLabel(virusTotal.status)}
              </span>
            </div>
            {renderFeedCardContent(virusTotal, () => (
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
            ))}
          </div>
          {virusTotal.status === 'success' && (
            <div className="pt-4 mt-4 border-t border-[#1a2336]/60 flex justify-between items-center text-[10.5px] min-w-0">
              <span className="text-slate-500 font-bold uppercase tracking-widest text-[9.5px] truncate">Severity Verdict</span>
              <span className="px-2.5 py-1 rounded font-mono font-bold uppercase bg-rose-950/20 text-rose-400 border border-rose-850/30 flex-shrink-0 h-5.5 flex items-center justify-center">
                {virusTotal.riskLevel}
              </span>
            </div>
          )}
        </div>

        {/* PhishTank Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full h-full min-w-0 overflow-hidden">
          <div className="space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2.5 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">PhishTank Ingestion</span>
              <span className={getStatusBadgeClass(phishTank.status)}>
                {getStatusBadgeLabel(phishTank.status)}
              </span>
            </div>
            {renderFeedCardContent(phishTank, () => (
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
            ))}
          </div>
          {phishTank.status === 'success' && (
            <div className="pt-4 mt-4 border-t border-[#1a2336]/60 flex justify-between items-center text-[10.5px] min-w-0">
              <span className="text-slate-500 font-bold uppercase tracking-widest text-[9.5px] truncate">Scoring Confidence</span>
              <span className="px-2.5 py-1 rounded font-mono font-bold uppercase bg-brand-950/20 text-brand-400 border border-brand-850/30 flex-shrink-0 h-5.5 flex items-center justify-center">
                {phishTank.confidence}
              </span>
            </div>
          )}
        </div>

        {/* URLHaus Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full h-full min-w-0 overflow-hidden">
          <div className="space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2.5 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">URLHaus Database</span>
              <span className={getStatusBadgeClass(urlHaus.status)}>
                {getStatusBadgeLabel(urlHaus.status)}
              </span>
            </div>
            {renderFeedCardContent(urlHaus, () => (
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
            ))}
          </div>
          {urlHaus.status === 'success' && (
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
          )}
        </div>

        {/* AbuseIPDB Card */}
        <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl hover:border-slate-700/60 hover:-translate-y-0.5 transition-all duration-300 shadow-sm flex flex-col justify-between w-full h-full min-w-0 overflow-hidden">
          <div className="space-y-4 min-w-0">
            <div className="flex items-center justify-between border-b border-[#1a2336]/40 pb-2.5 min-w-0">
              <span className="text-xs font-black text-slate-200 font-sans tracking-wide truncate">AbuseIPDB Registry</span>
              <span className={getStatusBadgeClass(abuseIPDB.status)}>
                {getStatusBadgeLabel(abuseIPDB.status)}
              </span>
            </div>
            {renderFeedCardContent(abuseIPDB, () => (
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
            ))}
          </div>
          {abuseIPDB.status === 'success' && (
            <div className="pt-4 mt-4 border-t border-[#1a2336]/60 flex justify-between items-center text-[10.5px] min-w-0">
              <span className="text-slate-500 font-bold uppercase tracking-widest text-[9.5px] truncate">Abuse Confidence</span>
              <span className="px-2.5 py-1 rounded font-mono font-bold uppercase bg-rose-950/20 text-rose-400 border border-rose-850/30 animate-pulse flex-shrink-0 h-5.5 flex items-center justify-center">
                {abuseIPDB.abuseConfidence}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
