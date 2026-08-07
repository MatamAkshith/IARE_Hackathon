/**
 * Investigation Workspace Page — ThreatLens Frontend
 *
 * **Stage A.3 / A.4**: Wired to the live backend investigation pipeline.
 *
 * The URL submission triggers the full 9-step backend pipeline:
 *   Domain registration → Scan record → Feature extraction → Unified evidence
 *   → Risk evaluation → AI report → Result display
 *
 * UI state machine:
 *   idle      → URL input rendered, waiting for submission
 *   queued    → Scan queued, ScanStatus spinner starts
 *   scanning  → Backend pipeline actively running (5-30s for real URLs)
 *   completed → Results rendered: RiskSummary, BadgeGroup, ExplanationPanel, EvidenceAccordion
 *
 * Components are untouched — only data source changed from mock to live API.
 */

import React, { useState } from 'react'
import useScans from '../hooks/useScans'
import URLInputCard from '../components/investigation/URLInputCard'
import ScanStatus from '../components/investigation/ScanStatus'
import RiskSummary from '../components/investigation/RiskSummary'
import ExplanationPanel from '../components/investigation/ExplanationPanel'
import EvidenceAccordion from '../components/investigation/EvidenceAccordion'
import BadgeGroup from '../components/investigation/BadgeGroup'

export default function Investigation() {
  const [url, setUrl] = useState('')
  const { result, loading, status, error, triggerScan, clearScan } = useScans()

  const handleScan = () => {
    if (url.trim()) {
      triggerScan(url)
    }
  }

  const handleClear = () => {
    setUrl('')
    clearScan()
  }

  const isProcessing = status === 'queued' || status === 'scanning'

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
            disabled={isProcessing}
          />

          {status !== 'idle' && (
            <ScanStatus status={status} />
          )}

          {/* Backend pipeline latency notice during scan */}
          {status === 'scanning' && (
            <div className="border border-brand-900/40 bg-brand-950/10 rounded-xl p-4 text-xs text-brand-300 space-y-1">
              <div className="font-semibold uppercase tracking-wider text-brand-400 text-[10px]">
                ⚡ Live Pipeline Active
              </div>
              <p className="text-slate-400 leading-relaxed">
                Running WHOIS lookup, DNS resolution, TLS inspection, HTML analysis,
                and threat intelligence feeds. This may take 10–30 seconds for external URLs.
              </p>
            </div>
          )}
        </div>

        {/* Right Side Panel: Threat Reports (Visible when scan completes) */}
        <div className="lg:col-span-2">
          {error ? (
            <div className="border border-rose-900 bg-rose-950/10 p-6 rounded-xl shadow-md space-y-3">
              <div className="flex items-center gap-2 text-rose-400">
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="font-bold uppercase tracking-wider text-xs">Scan Pipeline Error</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{error}</p>
              <button
                type="button"
                onClick={handleClear}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-lg text-xs uppercase tracking-wider transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : result && status === 'completed' ? (
            <div className="space-y-6 animate-fade-in">
              {/* Live data badge */}
              <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-950/20 border border-emerald-900/30 rounded-lg w-fit">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse flex-shrink-0" />
                <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
                  Live Backend Result
                </span>
              </div>

              {/* Risk Summary and Findings Tags */}
              <div className="space-y-4">
                <RiskSummary risk={result.risk} />
                <BadgeGroup badges={result.badges} />
              </div>

              {/* Narratives and Accordions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                <div className="space-y-6">
                  <ExplanationPanel findings={result.explanation} />
                </div>
                <div className="space-y-6">
                  <EvidenceAccordion evidence={result.evidence} />
                </div>
              </div>
            </div>
          ) : (
            <div className="border border-dashed border-[#1a2336] rounded-xl p-12 text-center text-slate-500 text-xs bg-[#090d16]/10 flex flex-col items-center justify-center min-h-[300px] space-y-3">
              <svg className="w-8 h-8 text-slate-600 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>Submit a target URL in the workspace dashboard to extract telemetry metrics.</span>
              <span className="text-[10px] text-slate-600">
                Results are fetched live from the ThreatLens backend pipeline.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
