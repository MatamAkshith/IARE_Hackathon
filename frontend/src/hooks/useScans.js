import { useState } from 'react'
import { getInvestigation } from '../services/scanService'

/**
 * Custom hook to manage target inspections and scans status state machines.
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
export default function useScans() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)

  const triggerScan = async (url) => {
    setLoading(true)
    setError(null)
    setStatus('queued')

    // Simulated stepper step transitions
    try {
      await new Promise((resolve) => setTimeout(resolve, 300))
      setStatus('scanning')
      
      const scanResult = await getInvestigation(url)
      
      setStatus('completed')
      setResult(scanResult)
    } catch (err) {
      setError(err.message || 'Pipeline analysis failed.')
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
