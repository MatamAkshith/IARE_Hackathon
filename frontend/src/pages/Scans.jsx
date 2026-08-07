import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitInvestigation, getInvestigationHistory, getInvestigationStatus } from '../api'
import URLInputCard from '../components/investigation/URLInputCard'
import ScanStatus from '../components/investigation/ScanStatus'
import StatusPill from '../components/StatusPill'
import SkeletonLoader from '../components/SkeletonLoader'

/**
 * Scans Workspace — ThreatLens Frontend
 *
 * Stage A.3 — Submission & Workflow Integration.
 *
 * Implements:
 *  - Interactive URL input with pre-flight regex validation
 *  - Progress polling using polling loop checking status (pending -> scanning -> completed)
 *  - Interactive table displaying scan history fetched from getInvestigationHistory()
 *  - Automatic redirect to /scans/:id on scan completion
 */
export default function Scans() {
  const navigate = useNavigate()
  
  // State
  const [url, setUrl] = useState('')
  const [scans, setScans] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [scanError, setScanError] = useState(null)
  
  // Current active scan state
  const [activeScan, setActiveScan] = useState(null) // { id, status, url }
  const [activeStatus, setActiveStatus] = useState('idle') // idle, queued, scanning, completed
  
  // Ref for polling interval timer
  const pollTimerRef = useRef(null)

  // Fetch history list on mount
  const loadHistory = async () => {
    try {
      const data = await getInvestigationHistory()
      // Sort scans by ID descending to show latest first
      setScans(data.sort((a, b) => b.id - a.id))
    } catch (err) {
      console.error('Failed to load scans history:', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  useEffect(() => {
    loadHistory()
    return () => stopPolling()
  }, [])

  // Start polling scan status
  const startPolling = (scanId) => {
    stopPolling()
    pollTimerRef.current = setInterval(async () => {
      try {
        const check = await getInvestigationStatus(scanId)
        setActiveStatus(check.status)
        
        if (check.status === 'completed') {
          stopPolling()
          // Automatically route user to details page
          navigate(`/scans/${scanId}`)
        } else if (check.status === 'failed') {
          stopPolling()
          setScanError('Background extraction pipeline encountered a server-side error.')
          setActiveScan(null)
          setActiveStatus('idle')
          loadHistory()
        }
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 1000) // Poll every 1 second
  }

  // Clear polling timer
  const stopPolling = () => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current)
      pollTimerRef.current = null
    }
  }

  // Submission handler
  const handleScanSubmit = async () => {
    if (!url.trim()) return
    setScanError(null)
    setActiveStatus('queued')
    
    try {
      const scanObj = await submitInvestigation(url)
      setActiveScan(scanObj)
      startPolling(scanObj.id)
    } catch (err) {
      setScanError(err.message || 'Failed to submit target URL for scan.')
      setActiveStatus('idle')
      setActiveScan(null)
    }
  }

  const handleClearForm = () => {
    setUrl('')
    setScanError(null)
    setActiveScan(null)
    setActiveStatus('idle')
    stopPolling()
  }

  const isScanning = activeStatus === 'queued' || activeStatus === 'scanning'

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Domain Scanning Queue</h1>
        <p className="text-xs text-slate-400">
          Submit target URLs to analyze active threat indicators and monitor pipeline history records.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left Side Panel: Inputs and Stepper Status */}
        <div className="lg:col-span-1 space-y-6">
          <URLInputCard
            value={url}
            onChange={setUrl}
            onScan={handleScanSubmit}
            onClear={handleClearForm}
            disabled={isScanning}
          />

          {isScanning && (
            <ScanStatus status={activeStatus} />
          )}

          {activeStatus === 'scanning' && (
            <div className="border border-brand-900/40 bg-brand-950/10 rounded-xl p-4 text-xs text-brand-300 space-y-1 animate-pulse">
              <div className="font-semibold uppercase tracking-wider text-brand-400 text-[10px]">
                ⚡ Live Pipeline Active
              </div>
              <p className="text-slate-400 leading-relaxed">
                Ingesting WHOIS registrar details, querying DNS records, validating SSL certificates,
                and fetching external threat intelligence verdicts...
              </p>
            </div>
          )}

          {scanError && (
            <div className="border border-rose-900 bg-rose-950/10 p-5 rounded-xl text-xs text-rose-400 shadow-md space-y-2">
              <div className="font-bold uppercase tracking-wider text-[10px] text-rose-500">
                Pipeline Scan Error
              </div>
              <p className="text-slate-400">{scanError}</p>
            </div>
          )}
        </div>

        {/* Right Side Panel: Telemetry Queue History Table */}
        <div className="lg:col-span-2 space-y-6">
          <div className="border border-[#1a2336] bg-[#090d16] rounded-xl overflow-hidden shadow-md">
            <div className="px-5 py-4 border-b border-[#1a2336] bg-[#0c121e]/80 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7 a 2 2 0 0 0 -2 2 v12 a 2 2 0 0 0 2 2 h10 a 2 2 0 0 0 2 -2 V7 a 2 2 0 0 0 -2 -2 h-2 M9 5 a 2 2 0 0 0 2 2 h2 a 2 2 0 0 0 2 -2 M9 5 a 2 2 0 0 1 2 -2 h2 a 2 2 0 0 1 2 2" />
                </svg>
                <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Domain Ingestion Log</h3>
              </div>
              <button
                type="button"
                onClick={loadHistory}
                className="text-[10px] uppercase font-bold text-brand-400 hover:text-brand-300 transition-colors"
              >
                Refresh Log
              </button>
            </div>

            <div className="overflow-x-auto">
              {loadingHistory ? (
                <div className="p-8">
                  <SkeletonLoader />
                </div>
              ) : (
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-[#0b0f19] border-b border-[#1a2336] text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                      <th className="py-3 px-5">Target Domain</th>
                      <th className="py-3 px-5">Status</th>
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
                            {scan.campaign_id ? (
                              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-brand-900/35 text-brand-300 border border-brand-800/40">
                                Campaign Linked
                              </span>
                            ) : (
                              <span className="text-slate-500 font-mono text-[10px] italic">Unattributed</span>
                            )}
                          </td>
                          <td className="py-3.5 px-5 text-right font-mono text-slate-500 text-[10px]">
                            {scan.scanTime}
                          </td>
                          <td className="py-3.5 px-5 text-center">
                            {scan.status === 'completed' ? (
                              <button
                                type="button"
                                onClick={() => navigate(`/scans/${scan.id}`)}
                                className="px-2.5 py-1 rounded bg-[#0e1422] border border-[#1a2336] hover:border-brand-500 text-brand-400 hover:text-brand-300 font-bold transition-all text-[10px] uppercase"
                              >
                                View Details
                              </button>
                            ) : (
                              <span className="text-slate-600 text-[10px] font-semibold select-none">—</span>
                            )}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="py-8 text-center text-slate-500 font-medium">
                          No scans in queue. Submit a URL above to start.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
