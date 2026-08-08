import React from 'react'
import { useNavigate } from 'react-router-dom'
import StatusPill from '../StatusPill'
import SkeletonLoader from '../SkeletonLoader'

const getCampaignBadgeColor = (name) => {
  if (!name) return 'bg-slate-900/30 text-slate-400 border-slate-800';
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % 4;
  const colors = [
    'bg-brand-950/20 text-brand-400 border-brand-900/30 hover:border-brand-500 hover:text-brand-300',
    'bg-purple-950/20 text-purple-400 border-purple-900/30 hover:border-purple-500 hover:text-purple-300',
    'bg-amber-950/20 text-amber-400 border-amber-900/30 hover:border-amber-500 hover:text-amber-300',
    'bg-teal-950/20 text-teal-400 border-teal-900/30 hover:border-teal-500 hover:text-teal-300'
  ];
  return colors[index];
};

export default function ScanTable({ scans = [], loading = false, onRetry }) {
  const navigate = useNavigate()

  const getScoreBadge = (scan) => {
    if (scan.status === 'failed') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded border text-[10px] font-semibold bg-rose-950/20 text-rose-400 border-rose-800/40" title="Analysis pipeline failed due to network timeout or service crash.">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
          FAILED
        </span>
      )
    }
    if (scan.status === 'pending' || scan.status === 'scanning') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-400 animate-pulse border border-slate-700/50">
          Calculating...
        </span>
      )
    }
    if (scan.overall_score === null || scan.overall_score === undefined) {
      return <span className="text-slate-500 font-mono text-[10px]">—</span>
    }
    const scoreVal = Number(scan.overall_score)
    let colorClass = ''
    let label = ''
    if (scoreVal <= 20) {
      colorClass = 'bg-emerald-950/30 text-emerald-400 border-emerald-800/40'
      label = 'SAFE'
    } else if (scoreVal <= 70) {
      colorClass = 'bg-amber-950/30 text-amber-400 border-amber-800/40'
      label = 'MEDIUM'
    } else if (scoreVal <= 90) {
      colorClass = 'bg-orange-950/30 text-orange-400 border-orange-800/40'
      label = 'HIGH'
    } else {
      colorClass = 'bg-rose-950/30 text-rose-400 border-rose-800/40'
      label = 'CRITICAL'
    }
    return (
      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${colorClass}`}>
        {Math.round(scoreVal)} {label}
      </span>
    )
  }

  return (
    <div className="border border-[#1a2336] bg-[#090d16] rounded-xl overflow-hidden shadow-md">
      <div className="px-5 py-4 border-b border-[#1a2336] bg-[#0c121e]/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7 a 2 2 0 0 0 -2 2 v12 a 2 2 0 0 0 2 2 h10 a 2 2 0 0 0 2 -2 V7 a 2 2 0 0 0 -2 -2 h-2 M9 5 a 2 2 0 0 0 2 2 h2 a 2 2 0 0 0 2 -2 M9 5 a 2 2 0 0 1 2 -2 h2 a 2 2 0 0 1 2 2" />
          </svg>
          <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Domain Ingestion Log</h3>
        </div>
      </div>

      <div className="overflow-x-auto">
        {loading ? (
          <div className="p-8">
            <SkeletonLoader />
          </div>
        ) : (
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#0b0f19] border-b border-[#1a2336] text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-5">Target Domain</th>
                <th className="py-3 px-5">Status</th>
                <th className="py-3 px-5">Risk Score</th>
                <th className="py-3 px-5">Attribution</th>
                <th className="py-3 px-5 text-right">Time Ingested</th>
                <th className="py-3 px-5 text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              {scans.length > 0 ? (
                scans.map((scan) => (
                  <tr
                    key={scan.id}
                    className="border-b border-[#151d2c] last:border-b-0 hover:bg-[#101726]/40 transition-colors"
                  >
                    <td className="py-3.5 px-5 font-mono text-[11px] font-semibold text-slate-300 select-all truncate max-w-[200px]" title={scan.domain}>
                      {scan.domain}
                    </td>
                    <td className="py-3.5 px-5">
                      <StatusPill status={scan.status} />
                    </td>
                    <td className="py-3.5 px-5">
                      {getScoreBadge(scan)}
                    </td>
                    <td className="py-3.5 px-5">
                      {scan.campaign_name ? (
                        <button
                          type="button"
                          onClick={() => navigate(`/campaigns?campaignId=${scan.campaign_uid || scan.campaign_id}`)}
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold border transition-all cursor-pointer text-left truncate max-w-[150px] ${getCampaignBadgeColor(scan.campaign_name)}`}
                          title={`View Campaign: ${scan.campaign_name}`}
                        >
                          {scan.campaign_name}
                        </button>
                      ) : (
                        <span className="text-slate-500 font-mono text-[10px] italic">Unattributed</span>
                      )}
                    </td>
                    <td className="py-3.5 px-5 text-right font-mono text-slate-500 text-[10px]">
                      {scan.scanTime}
                    </td>
                    <td className="py-3.5 px-5 text-center">
                      {scan.status === 'completed' ? (
                        <div className="flex items-center justify-center gap-2">
                          <button
                            type="button"
                            onClick={() => navigate(`/scans/${scan.id}`)}
                            className="px-2.5 py-1 rounded bg-[#0e1422] border border-[#1a2336] hover:border-brand-500 text-brand-400 hover:text-brand-300 font-bold transition-all text-[10px] uppercase"
                          >
                            Details
                          </button>
                          <button
                            type="button"
                            onClick={() => navigate(`/reports?scanId=${scan.id}`)}
                            className="px-2.5 py-1 rounded bg-[#0e1422] border border-[#1a2336] hover:border-rose-600 text-rose-400 hover:text-rose-300 font-bold transition-all text-[10px] uppercase"
                            title="View Intelligence Report"
                          >
                            Report
                          </button>
                        </div>
                      ) : scan.status === 'pending' || scan.status === 'scanning' ? (
                        <div className="flex items-center justify-center">
                          <button
                            type="button"
                            disabled
                            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#0e1422] border border-[#1a2336] text-slate-500 font-bold text-[10px] uppercase cursor-not-allowed select-none"
                          >
                            <svg className="animate-spin h-3.5 w-3.5 text-brand-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Analyzing
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center">
                          <button
                            type="button"
                            onClick={() => onRetry && onRetry(scan.domain)}
                            className="px-2.5 py-1 rounded border border-rose-900 bg-rose-950/20 text-rose-400 hover:text-rose-300 font-bold text-[10px] uppercase transition-all"
                            title="Retry submitting this domain for threat analysis"
                          >
                            Retry
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-500 font-medium">
                    No scans in queue. Submit a URL above to start.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
