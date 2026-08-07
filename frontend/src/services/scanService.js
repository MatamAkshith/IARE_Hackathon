/**
 * Scan Service — ThreatLens Frontend
 *
 * **Stage A.3**: Replaced mock data with live backend investigation pipeline.
 *
 * This service is consumed by the `useScans` hook, which drives the
 * Investigation page workflow. The call chain is:
 *
 *   useScans → getInvestigation(url)
 *     → runInvestigation(url) [api/investigationApiService.js]
 *       → domain + scan creation → extraction → evidence → risk → AI report
 *     → adaptScanData(result) [adapters/scanAdapter.js]
 *     → InvestigationResult → React components
 *
 * @module services/scanService
 */

import { runInvestigation, validateAndNormalizeUrl, getInvestigationHistory } from '../api/investigationApiService.js'
import { adaptScanData } from '../adapters/scanAdapter.js'

/**
 * Validates, submits, and runs the full investigation pipeline for a URL.
 * Returns a normalized InvestigationResult ready for the Investigation components.
 *
 * @param {string} url - Raw URL string from the input field
 * @returns {Promise<import('../interfaces').InvestigationResult>}
 * @throws {import('../api/types').ApiError | Error} On validation failure or backend error
 */
export async function getInvestigation(url) {
  // Frontend URL validation before hitting the backend
  const { valid, normalized, error } = validateAndNormalizeUrl(url)
  if (!valid) {
    const validationError = new Error(error)
    validationError.code = 'VALIDATION_ERROR'
    throw validationError
  }

  // Run the full backend pipeline
  const result = await runInvestigation(normalized)

  // Normalize through the adapter to preserve the shape expected by components
  return adaptScanData(result)
}

/**
 * Retrieves the recent scan history list from the backend.
 *
 * @returns {Promise<Array>} List of raw ScanResponse records
 */
export async function getScanHistory() {
  return getInvestigationHistory()
}

export default { getInvestigation, getScanHistory }
