import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitInvestigation, getInvestigationHistory, getInvestigationStatus } from '../api'
import URLInputCard from '../components/investigation/URLInputCard'
import ScanStatus from '../components/investigation/ScanStatus'
import ScanTable from '../components/scans/ScanTable'

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
          <div className="flex justify-end mb-2">
            <button
              type="button"
              onClick={loadHistory}
              className="text-[10px] uppercase font-bold text-brand-400 hover:text-brand-300 transition-colors"
            >
              Refresh Log
            </button>
          </div>
          <ScanTable
            scans={scans}
            loading={loadingHistory}
            onRetry={(domain) => setUrl(domain)}
          />
        </div>
      </div>
    </div>
  )
}
