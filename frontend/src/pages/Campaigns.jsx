import React, { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import SkeletonLoader from '../components/SkeletonLoader'
import CampaignSummaryCard from '../components/campaign/CampaignSummaryCard'
import RelationshipGraph from '../components/campaign/RelationshipGraph'
import ConnectedDomainsTable from '../components/campaign/ConnectedDomainsTable'
import InfrastructureCard from '../components/campaign/InfrastructureCard'
import EvidenceTable from '../components/campaign/EvidenceTable'
import ConfidenceCard from '../components/campaign/ConfidenceCard'
import CampaignTimeline from '../components/campaign/CampaignTimeline'
import { getCampaignsList, getCampaignDetails } from '../api/campaignService.js'

const SEVERITY_COLOR = {
  critical: 'text-rose-400 bg-rose-950/20 border-rose-800/40',
  high: 'text-amber-400 bg-amber-950/20 border-amber-800/40',
  medium: 'text-yellow-400 bg-yellow-950/20 border-yellow-800/40',
  low: 'text-emerald-400 bg-emerald-950/20 border-emerald-800/40',
  safe: 'text-slate-400 bg-slate-800/20 border-slate-700/40',
}

export default function Campaigns() {
  const [searchParams, setSearchParams] = useSearchParams()

  // Campaign list for dropdown
  const [campaignList, setCampaignList] = useState([])
  const [listLoading, setListLoading] = useState(true)

  // Selected campaign detail state
  const [selectedCampaignId, setSelectedCampaignId] = useState(null)
  const [campaignData, setCampaignData] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState(null)

  // Load campaign list on mount
  useEffect(() => {
    async function loadList() {
      setListLoading(true)
      try {
        const list = await getCampaignsList(0, 50)
        const sorted = (list || []).sort((a, b) => b.campaign_id.localeCompare(a.campaign_id))
        setCampaignList(sorted)

        // Determine initial selection from URL params or first campaign
        const paramId = searchParams.get('campaignId') || searchParams.get('id')
        const initialId = paramId || (sorted.length > 0 ? sorted[0].campaign_id : null)
        if (initialId) setSelectedCampaignId(initialId)
      } catch (err) {
        console.error('[Campaigns] Failed to load campaign list:', err)
      } finally {
        setListLoading(false)
      }
    }
    loadList()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Load campaign details whenever selectedCampaignId changes
  const loadDetail = useCallback(async (campId) => {
    if (!campId) return
    setDetailLoading(true)
    setDetailError(null)
    try {
      const data = await getCampaignDetails(campId)
      setCampaignData(data)
    } catch (err) {
      console.error('[Campaigns] Failed to load campaign detail:', campId, err)
      setDetailError(err?.message || 'Failed to load campaign details.')
    } finally {
      setDetailLoading(false)
    }
  }, [])

  useEffect(() => {
    if (selectedCampaignId) {
      setSearchParams({ campaignId: selectedCampaignId }, { replace: true })
      loadDetail(selectedCampaignId)
    }
  }, [selectedCampaignId]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleCampaignChange = (e) => {
    setSelectedCampaignId(e.target.value)
  }

  const selectedMeta = campaignList.find(c => c.campaign_id === selectedCampaignId)

  if (listLoading) return <SkeletonLoader />

  const { summary, connectedDomains, infrastructure, sharedEvidence, confidence, timeline } = campaignData || {}

  return (
    <div className="space-y-6">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Campaign Correlation &amp; Attribution</h1>
          <p className="text-xs text-slate-400">
            Analyze malicious campaign clusters, group domain footprints by nameservers, and map coordinated infrastructure links.
          </p>
        </div>

        {/* Campaign Selector Dropdown */}
        <div className="flex-shrink-0 sm:min-w-[360px]">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="campaign-selector" className="text-[10px] font-bold uppercase text-slate-500 tracking-wider">
              Active Campaign
            </label>
            <div className="relative">
              <select
                id="campaign-selector"
                value={selectedCampaignId || ''}
                onChange={handleCampaignChange}
                disabled={campaignList.length === 0 || detailLoading}
                className="w-full appearance-none bg-[#0d1322] border border-[#1a2336] text-slate-200 text-xs font-mono px-4 py-2.5 pr-10 rounded-lg cursor-pointer hover:border-brand-500 focus:outline-none focus:border-brand-400 focus:ring-1 focus:ring-brand-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {campaignList.length === 0 ? (
                  <option value="">No campaigns available</option>
                ) : (
                  campaignList.map(c => (
                    <option key={c.campaign_id} value={c.campaign_id}>
                      {c.campaign_id} — {c.name}
                    </option>
                  ))
                )}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3">
                {detailLoading ? (
                  <svg className="animate-spin h-3.5 w-3.5 text-brand-400" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                ) : (
                  <svg className="h-3.5 w-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                )}
              </div>
            </div>
            {selectedMeta && (
              <div className="flex items-center gap-2">
                <span className={`px-1.5 py-0.5 rounded border text-[9px] font-bold uppercase tracking-wider ${SEVERITY_COLOR[selectedMeta.severity] || SEVERITY_COLOR.low}`}>
                  {selectedMeta.severity}
                </span>
                <span className="text-[9px] text-slate-600 font-mono">
                  {selectedMeta.members?.length ?? 0} domain(s) correlated
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Error banner */}
      {detailError && (
        <div className="border border-rose-900 bg-rose-950/10 p-4 rounded-xl text-xs text-rose-400 flex items-center gap-3">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{detailError}</span>
          <button
            type="button"
            onClick={() => loadDetail(selectedCampaignId)}
            className="ml-auto text-[10px] font-bold uppercase text-rose-400 hover:text-rose-300 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Content */}
      {detailLoading ? (
        <div className="opacity-60 pointer-events-none">
          <SkeletonLoader />
        </div>
      ) : campaignData ? (
        <>
          {/* Campaign Summary overview */}
          <CampaignSummaryCard summary={summary} />

          {/* Grid panels */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {/* Left Side: Topology Visualizer, Connected Domains, and Evidence log */}
            <div className="lg:col-span-2 space-y-6">
              <RelationshipGraph campaignId={summary.campaignId} />
              <ConnectedDomainsTable domains={connectedDomains} />
              <EvidenceTable evidence={sharedEvidence} />
            </div>

            {/* Right Side: Verdict Engine, Shared Infrastructure, and History Timeline */}
            <div className="space-y-6">
              <ConfidenceCard confidence={confidence} />
              <InfrastructureCard infrastructure={infrastructure} />
              <CampaignTimeline timeline={timeline} />
            </div>
          </div>
        </>
      ) : !detailError && (
        <div className="flex flex-col items-center justify-center py-24 text-slate-500 gap-2">
          <svg className="w-10 h-10 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-3-3v6M12 3C7.03 3 3 7.03 3 12s4.03 9 9 9 9-4.03 9-9-4.03-9-9-9z" />
          </svg>
          <p className="text-sm font-medium">Select a campaign above to view details.</p>
        </div>
      )}
    </div>
  )
}
