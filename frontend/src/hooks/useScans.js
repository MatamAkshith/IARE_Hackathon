/**
 * useScans — Investigation workflow hook — ThreatLens Frontend
 *
 * **Stage A.3**: Updated to call the live backend investigation pipeline.
 *
 * Manages the investigation state machine:
 *   idle → queued → scanning → completed
 *   idle → queued → error (on failure)
 *
 * The hook no longer uses mock delays. Real backend pipeline execution
 * drives the status transitions. The `scanning` state is maintained
 * throughout the actual backend calls (which take 5-30s for real URLs).
 *
 * @returns {{
 *   result: import('../interfaces').InvestigationResult|null,
 *   loading: boolean,
 *   status: 'idle'|'queued'|'scanning'|'completed',
 *   error: string|null,
 *   triggerScan: Function,
 *   clearScan: Function
 * }}
 */

import { useState } from 'react'
import { getInvestigation } from '../services/scanService'
import { isApiError } from '../api/index.js'

/**
 * Extracts a display-safe error message from any thrown value.
 *
 * @param {unknown} err
 * @returns {string}
 */
function extractMessage(err) {
  if (isApiError(err)) return err.message
  if (err instanceof Error) return err.message
  if (typeof err === 'string') return err
  return 'An unexpected error occurred during pipeline analysis.'
}

export default function useScans() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)

  const triggerScan = async (url) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setStatus('queued')

    try {
      // Brief delay to allow the UI to render the 'queued' state
      await new Promise((resolve) => setTimeout(resolve, 150))
      setStatus('scanning')

      // Run the full backend pipeline (this is the real API call)
      const scanResult = await getInvestigation(url)

      setStatus('completed')
      setResult(scanResult)
    } catch (err) {
      setError(extractMessage(err))
      setStatus('idle')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const clearScan = () => {
    setResult(null)
    setStatus('idle')
    setError(null)
  }

  return {
    result,
    loading,
    status,
    error,
    triggerScan,
    clearScan
  }
}
