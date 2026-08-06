import { delay } from './mockApi'
import { threatIntelligenceData } from '../data/threatIntelligenceData'
import { adaptReportData } from '../adapters/reportAdapter'

/**
 * Service to retrieve threat feeds and reporting summaries.
 * 
 * @returns {Promise<ThreatFeedData>}
 */
export async function getReports() {
  await delay(500, 800)
  
  if (sessionStorage.getItem('mock_report_error') === 'true') {
    throw new Error('Failed to retrieve external threat feeds registries.')
  }
  
  return adaptReportData(threatIntelligenceData)
}

export default { getReports }
