import React, { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import ThreatFeedPanel from '../components/reports/ThreatFeedPanel'
import IOCTable from '../components/reports/IOCTable'
import ReputationCard from '../components/reports/ReputationCard'
import RecommendationsPanel from '../components/reports/RecommendationsPanel'
import IncidentReportPreview from '../components/reports/IncidentReportPreview'
import ExportPreview from '../components/reports/ExportPreview'
import SkeletonLoader from '../components/SkeletonLoader'
import ErrorFallback from '../components/ErrorFallback'
import { getInvestigationHistory } from '../api/investigationService.js'
import { getReportForScan } from '../services/reportService.js'
import { adaptReportData } from '../adapters/reportAdapter.js'

const EMPTY_REPORT = adaptReportData({
  threatFeeds: {
    virustotal: { name: 'VirusTotal', status: 'Inactive', verdict: 'No data' },
    phishtank: { name: 'PhishTank', status: 'Inactive', verdict: 'No data' },
    urlhaus: { name: 'URLHaus', status: 'Inactive', verdict: 'No data' },
    abuseipdb: { name: 'AbuseIPDB', status: 'Inactive', verdict: 'No data' }
  },
  iocs: [],
  reputation: { verdict: 'Unknown', riskLevel: 'low', score: 0, maxScore: 100, confidence: '0%', recommendation: 'No scans run.' },
  recommendations: [],
  reportPreview: { title: 'Incident Report Preview', executiveSummary: 'No active threat target has been scanned yet.' },
  exportOptions: [{ id: 'MD', name: 'Markdown (.md)', desc: 'Export evidence details' }]
})

export default function Reports() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  // Scan selector state
  const [completedScans, setCompletedScans] = useState([]) // [{ id, domain, status, scanTime }]
  const [scansLoading, setScansLoading] = useState(true)

  // Report content state
  const [selectedScanId, setSelectedScanId] = useState(null)
  const [reports, setReports] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [reportError, setReportError] = useState(null)

  // Load completed scans list on mount
  useEffect(() => {
    async function loadScans() {
      setScansLoading(true)
      try {
        const history = await getInvestigationHistory()
        const completed = (history || [])
          .filter(s => s.status === 'completed')
          .sort((a, b) => b.id - a.id)
        setCompletedScans(completed)

        // Determine initial selection from URL params or latest scan
        const paramId = searchParams.get('scanId') ? Number(searchParams.get('scanId')) : null
        const initialId = paramId || (completed.length > 0 ? completed[0].id : null)
        if (initialId) setSelectedScanId(initialId)
      } catch (err) {
        console.error('[Reports] Failed to load scan history:', err)
        setReports(EMPTY_REPORT)
      } finally {
        setScansLoading(false)
      }
    }
    loadScans()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch report whenever selectedScanId changes
  const loadReport = useCallback(async (scanId) => {
    if (!scanId) {
      setReports(EMPTY_REPORT)
      return
    }
    setReportLoading(true)
    setReportError(null)
    try {
      const data = await getReportForScan(scanId)
      setReports(data)
    } catch (err) {
      console.error('[Reports] Failed to load report for scan:', scanId, err)
      setReportError(err?.message || 'Failed to load report for this scan.')
    } finally {
      setReportLoading(false)
    }
  }, [])

  useEffect(() => {
    if (selectedScanId) {
      // Sync URL param
      setSearchParams({ scanId: String(selectedScanId) }, { replace: true })
      loadReport(selectedScanId)
    }
  }, [selectedScanId]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleScanChange = (e) => {
    const id = Number(e.target.value)
    setSelectedScanId(id)
  }

  const selectedScan = completedScans.find(s => s.id === selectedScanId)

  // Severity helper for dropdown label
  const getSeverityLabel = (scan) => {
    if (!scan) return ''
    // we don't have severity here, just show id + domain
    return `#${scan.id} — ${scan.domain}`
  }

  // Show full skeleton if scans list is still loading
  if (scansLoading) return <SkeletonLoader />

  const { threatFeeds, iocs, reputation, recommendations, reportPreview, exportOptions } = reports || EMPTY_REPORT

  return (
    <div className="space-y-6">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Threat Intelligence &amp; Reports</h1>
          <p className="text-xs text-slate-400">
            Analyze reputation scores from third-party intel databases, track IOC tags, and preview formatted incident reports.
          </p>
        </div>

        {/* Scan Selector Dropdown */}
        <div className="flex-shrink-0 sm:min-w-[340px]">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="scan-selector" className="text-[10px] font-bold uppercase text-slate-500 tracking-wider">
              Historical Investigation
            </label>
            <div className="relative">
              <select
                id="scan-selector"
                value={selectedScanId || ''}
                onChange={handleScanChange}
                disabled={completedScans.length === 0 || reportLoading}
                className="w-full appearance-none bg-[#0d1322] border border-[#1a2336] text-slate-200 text-xs font-mono px-4 py-2.5 pr-10 rounded-lg cursor-pointer hover:border-brand-500 focus:outline-none focus:border-brand-400 focus:ring-1 focus:ring-brand-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {completedScans.length === 0 ? (
                  <option value="">No completed scans available</option>
                ) : (
                  completedScans.map(scan => (
                    <option key={scan.id} value={scan.id}>
                      {getSeverityLabel(scan)}
                    </option>
                  ))
                )}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3">
                {reportLoading ? (
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
            {selectedScan && (
              <div className="flex items-center gap-2">
                <span className="text-[9px] text-slate-600 font-mono">Ingested: {selectedScan.scanTime}</span>
                <span className="text-slate-700">•</span>
                <button
                  type="button"
                  onClick={() => navigate(`/scans/${selectedScan.id}`)}
                  className="text-[9px] text-brand-400 hover:text-brand-300 font-bold uppercase tracking-wider transition-colors"
                >
                  View Investigation Details →
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Report error banner */}
      {reportError && (
        <div className="border border-rose-900 bg-rose-950/10 p-4 rounded-xl text-xs text-rose-400 flex items-center gap-3">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{reportError}</span>
          <button
            type="button"
            onClick={() => loadReport(selectedScanId)}
            className="ml-auto text-[10px] font-bold uppercase text-rose-400 hover:text-rose-300 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading overlay on report content */}
      {reportLoading ? (
        <div className="opacity-60 pointer-events-none">
          <SkeletonLoader />
        </div>
      ) : (
        /* Grid panels */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          {/* Left Side */}
          <div className="lg:col-span-2 space-y-6">
            <ThreatFeedPanel feeds={threatFeeds} />
            <IOCTable iocs={iocs} />
            <IncidentReportPreview report={reportPreview} />
          </div>

          {/* Right Side */}
          <div className="space-y-6">
            <ReputationCard reputation={reputation} />
            <RecommendationsPanel recommendations={recommendations} />
            <ExportPreview options={exportOptions} report={reportPreview} />
          </div>
        </div>
      )}
    </div>
  )
}
