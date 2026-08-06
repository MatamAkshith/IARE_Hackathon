import React, { useState } from 'react'
import { investigationData } from '../data/investigationData'
import URLInputCard from '../components/investigation/URLInputCard'
import ScanStatus from '../components/investigation/ScanStatus'
import RiskSummary from '../components/investigation/RiskSummary'
import ExplanationPanel from '../components/investigation/ExplanationPanel'
import EvidenceAccordion from '../components/investigation/EvidenceAccordion'
import BadgeGroup from '../components/investigation/BadgeGroup'

export default function Investigation() {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState('idle') // idle, queued, scanning, completed
  const [showResults, setShowResults] = useState(false)

  const handleScan = () => {
    setStatus('queued')
    setShowResults(false)

    // Simulate pre-flight check loader delay
    setTimeout(() => {
      setStatus('scanning')
      
      // Simulate extraction pipeline query delay
      setTimeout(() => {
        setStatus('completed')
        setShowResults(true)
      }, 700)

    }, 300)
  }

  const handleClear = () => {
    setUrl('')
    setStatus('idle')
    setShowResults(false)
  }

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">URL Investigation Workspace</h1>
        <p className="text-xs text-slate-400">
          Enter a suspicious URL to run pre-flight indicators checks and evaluate risk vectors.
        </p>
      </div>

      {/* Grid container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left Side Panel: Inputs and Stepper Status */}
        <div className="lg:col-span-1 space-y-6">
          <URLInputCard
            value={url}
            onChange={setUrl}
            onScan={handleScan}
            onClear={handleClear}
            disabled={status !== 'idle' && status !== 'completed'}
          />

          {status !== 'idle' && (
            <ScanStatus status={status} />
          )}
        </div>

        {/* Right Side Panel: Threat Reports (Visible when scan completes) */}
        <div className="lg:col-span-2">
          {showResults ? (
            <div className="space-y-6 animate-fade-in">
              {/* Risk Summary and Findings Tags */}
              <div className="space-y-4">
                <RiskSummary risk={investigationData.risk} />
                <BadgeGroup badges={investigationData.badges} />
              </div>

              {/* Narratives and Accordions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                <div className="space-y-6">
                  <ExplanationPanel findings={investigationData.explanation} />
                </div>
                <div className="space-y-6">
                  <EvidenceAccordion evidence={investigationData.evidence} />
                </div>
              </div>
            </div>
          ) : (
            <div className="border border-dashed border-[#1a2336] rounded-xl p-12 text-center text-slate-500 text-xs bg-[#090d16]/10 flex flex-col items-center justify-center min-h-[300px] space-y-3">
              <svg className="w-8 h-8 text-slate-600 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>Submit a target URL in the workspace dashboard to extract telemetry metrics.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
