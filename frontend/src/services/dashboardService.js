import { delay } from './mockApi'
import { dashboardData } from '../data/dashboardData'
import { adaptDashboardData } from '../adapters/dashboardAdapter'

/**
 * Service to retrieve main dashboard statistics.
 * 
 * @returns {Promise<DashboardData>}
 */
export async function getDashboard() {
  await delay(300, 600)
  
  // Support mock error simulation (e.g. if a flag is stored in session storage)
  if (sessionStorage.getItem('mock_dashboard_error') === 'true') {
    throw new Error('Failed to retrieve SOC dashboard telemetry.')
  }
  
  return adaptDashboardData(dashboardData)
}

export default { getDashboard }
