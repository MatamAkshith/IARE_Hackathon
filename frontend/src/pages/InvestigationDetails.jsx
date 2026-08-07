import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getInvestigationDetails } from '../api'
import SkeletonLoader from '../components/SkeletonLoader'
import ErrorFallback from '../components/ErrorFallback'
import RiskSummary from '../components/investigation/RiskSummary'
import BadgeGroup from '../components/investigation/BadgeGroup'
import ExplanationPanel from '../components/investigation/ExplanationPanel'
import EvidenceAccordion from '../components/investigation/EvidenceAccordion'

/**
 * Investigation Details View — ThreatLens Frontend
 *
 * Stage A.4 — Detailed Investigation View & Evidence Viewer.
 *
 * Fetches completed scan details by ID from the router path params,
 * and renders:
 *  - Interactive back controls to the /scans queue
 *  - Target summary header with scan status metadata
 *  - Explainable risk gauges (RiskSummary) & findings tags (BadgeGroup)
 *  - Detailed EvidenceAccordion collapsible tables
 *  - Suspicious indicator ExplanationPanel lists
 *  - Connected Campaign attribution panels
 *  - pre-generated AI Assistant reports (Analyst and Executive tabs)
 */
export default function InvestigationDetails() {
  const { id } = useParams()
  const navigate = useNavigate()

  // State
  const [details, setDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeReportTab, setActiveReportTab] = useState('analyst') // analyst, executive

  const fetchDetails = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getInvestigationDetails(Number(id))
      setDetails(data)
    } catch (err) {
      setError(err.message || 'Failed to retrieve detailed investigation payload.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (id) {
      fetchDetails()
    }
  }, [id])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-6 w-32 bg-slate-800 rounded animate-pulse" />
        <SkeletonLoader />
      </div>
    )
  }

  if (error) {
    return <ErrorFallback message={error} onRetry={fetchDetails} />
  }

  if (!details) {
    return (
      <div className="border border-dashed border-[#1a2336] rounded-xl p-12 text-center text-slate-500 text-xs">
        No investigation record found for target ID.
      </div>
    )
  }

  const { url, risk, explanation, badges, evidence, campaign, aiSummary } = details

  return (
    <div className="space-y-6">
      {/* Back Control Header */}
      <div className="flex flex-col gap-1 min-w-0">
        <button
          type="button"
          onClick={() => navigate('/scans')}
          className="flex items-center gap-1.5 text-slate-400 hover:text-brand-400 transition-colors text-xs uppercase font-extrabold tracking-wider w-fit"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Scanning Queue
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-2 min-w-0">
          <div className="min-w-0">
            <h1 className="text-xl font-bold tracking-tight text-slate-100 truncate font-mono select-all">
              {url}
            </h1>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Scan ID: {id} • Ingested Telemetry Indicators Records
            </p>
          </div>
          
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400 bg-emerald-950/20 px-2 py-0.5 border border-emerald-900/30 rounded">
              Report Compiled
            </span>
          </div>
        </div>
      </div>

      {/* Main split grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        
        {/* Left Columns: Risk Summary & Accordions */}
        <div className="lg:col-span-2 space-y-6">
          <div className="space-y-4">
            <RiskSummary risk={risk} />
            <BadgeGroup badges={badges} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
            <div className="space-y-6">
              <ExplanationPanel findings={explanation} />
              
              {/* Campaign Attribution Card (if present) */}
              {campaign ? (
                <div className="border border-brand-900/50 bg-brand-950/15 p-5 rounded-xl shadow-md space-y-4">
                  <div className="flex items-center gap-2 border-b border-brand-900/40 pb-3">
                    <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                    <h4 className="text-sm font-bold text-brand-300 tracking-wide uppercase">Campaign Attribution</h4>
                  </div>
                  
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-500 font-medium">Campaign:</span>
                      <span className="font-bold text-slate-200">{campaign.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500 font-medium">Severity:</span>
                      <span className="font-semibold text-rose-400 uppercase font-mono">{campaign.severity}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500 font-medium">Overlapping nodes:</span>
                      <span className="font-mono text-slate-200">{campaign.members.length} indicators</span>
                    </div>
                  </div>
                  
                  <button
                    type="button"
                    onClick={() => navigate('/campaigns')}
                    className="w-full py-2 bg-brand-900/40 hover:bg-brand-900/60 border border-brand-850/50 text-brand-300 hover:text-brand-200 text-[10px] font-bold uppercase tracking-wider rounded transition-colors"
                  >
                    View Campaign Topology Graph
                  </button>
                </div>
              ) : (
                <div className="border border-[#1a2336] bg-[#090d16]/30 p-5 rounded-xl text-center text-xs text-slate-500 py-6">
                  No overlapping infrastructure footprints correlated (Unattributed threat).
                </div>
              )}
            </div>
            
            <div className="space-y-6">
              <EvidenceAccordion evidence={evidence} />
            </div>
          </div>
        </div>

        {/* Right Column: AI Investigation Assistant pre-generated reports */}
        <div className="lg:col-span-1 space-y-6">
          <div className="border border-[#1a2336] bg-[#090d16] rounded-xl overflow-hidden shadow-md flex flex-col min-h-[400px]">
            {/* Header Tabs */}
            <div className="px-5 py-4 border-b border-[#1a2336] bg-[#0c121e]/80 flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <h3 className="font-semibold text-slate-200 text-sm tracking-wide">ThreatLens AI Assistant</h3>
              </div>
              
              <div className="flex bg-[#0e1422] p-0.5 rounded border border-[#172033] text-[9px] font-bold uppercase tracking-wide">
                <button
                  type="button"
                  onClick={() => setActiveReportTab('analyst')}
                  className={`px-2 py-1 rounded transition-colors ${
                    activeReportTab === 'analyst' ? 'bg-brand-900/50 text-brand-300' : 'text-slate-500 hover:text-slate-350'
                  }`}
                >
                  Analyst
                </button>
                <button
                  type="button"
                  onClick={() => setActiveReportTab('executive')}
                  className={`px-2 py-1 rounded transition-colors ${
                    activeReportTab === 'executive' ? 'bg-brand-900/50 text-brand-300' : 'text-slate-500 hover:text-slate-350'
                  }`}
                >
                  Executive
                </button>
              </div>
            </div>

            {/* Report Content Body */}
            <div className="p-5 flex-1 flex flex-col justify-between text-xs space-y-4">
              {activeReportTab === 'analyst' ? (
                aiSummary?.analyst ? (
                  <div className="space-y-4 animate-fade-in">
                    <div>
                      <span className="block text-[9px] uppercase font-extrabold text-slate-500 tracking-wider">
                        Technical Conclusion
                      </span>
                      <p className="text-slate-350 leading-relaxed font-sans font-medium mt-1">
                        {aiSummary.analyst.conclusion}
                      </p>
                    </div>

                    {aiSummary.analyst.risk_assessment_explanation && (
                      <div>
                        <span className="block text-[9px] uppercase font-extrabold text-slate-500 tracking-wider">
                          Risk Verdict Explanation
                        </span>
                        <p className="text-slate-350 leading-relaxed font-sans font-medium mt-1 italic">
                          "{aiSummary.analyst.risk_assessment_explanation}"
                        </p>
                      </div>
                    )}

                    {aiSummary.analyst.recommendations && (
                      <div className="space-y-2">
                        <span className="block text-[9px] uppercase font-extrabold text-slate-500 tracking-wider">
                          Containment Action Checklist
                        </span>
                        <ul className="space-y-1.5 pl-4 list-disc text-slate-400">
                          {(aiSummary.analyst.recommendations.immediate_actions || []).map((act, i) => (
                            <li key={i}>{act}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500 flex flex-col items-center justify-center space-y-2 flex-1">
                    <svg className="w-8 h-8 text-slate-650" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Analyst report pre-generation unavailable.</span>
                  </div>
                )
              ) : (
                aiSummary?.executive ? (
                  <div className="space-y-4 animate-fade-in">
                    <div>
                      <span className="block text-[9px] uppercase font-extrabold text-slate-500 tracking-wider">
                        Business Exposure Rating
                      </span>
                      <span className="text-rose-400 font-extrabold uppercase font-mono tracking-wider block mt-0.5 text-[11px]">
                        {aiSummary.executive.overall_risk_rating}
                      </span>
                    </div>

                    <div>
                      <span className="block text-[9px] uppercase font-extrabold text-slate-500 tracking-wider">
                        Business Impact Summary
                      </span>
                      <p className="text-slate-350 leading-relaxed font-sans font-medium mt-1">
                        {aiSummary.executive.business_impact}
                      </p>
                    </div>

                    {aiSummary.executive.recommended_action_summary && (
                      <div>
                        <span className="block text-[9px] uppercase font-extrabold text-slate-500 tracking-wider">
                          Recommended Actions Summary
                        </span>
                        <p className="text-slate-350 leading-relaxed font-sans font-medium mt-1">
                          {aiSummary.executive.recommended_action_summary}
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500 flex flex-col items-center justify-center space-y-2 flex-1">
                    <svg className="w-8 h-8 text-slate-650" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Executive summary pre-generation unavailable.</span>
                  </div>
                )
              )}

              {/* Notice Banner */}
              <div className="border-t border-[#1a2336] pt-4 text-[10px] text-slate-500 leading-tight">
                ⚡ Generated by provider-agnostic LLM reasoning gateway. Fallbacks active.
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
