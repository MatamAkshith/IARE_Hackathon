import { delay } from './mockApi'
import { investigationData } from '../data/investigationData'
import { adaptScanData } from '../adapters/scanAdapter'

/**
 * Service to execute URL inspections and retrieve telemetry.
 * 
 * @param {string} url Target URL string
 * @returns {Promise<InvestigationResult>}
 */
export async function getInvestigation(url) {
  // Simulates a longer latency for deep pipeline analysis
  await delay(800, 1200)
  
  if (sessionStorage.getItem('mock_scan_error') === 'true') {
    throw new Error('Pipeline extraction timeout occurred.')
  }
  
  // Return adapted mock investigation dataset
  return adaptScanData({
    ...investigationData,
    url: url || investigationData.url
  })
}

export default { getInvestigation }
