/**
 * Dashboard Service — ThreatLens Frontend
 *
 * **Stage A.2**: Replaced mock data source with live backend API calls.
 *
 * This service is consumed by `DataProvider.jsx` via `getDashboard()`.
 * The call chain is:
 *   DataProvider → getDashboard() → getDashboardData() [api/dashboardApiService.js]
 *   → adaptDashboardData() → DashboardData shape → React components
 *
 * The adapter contract (adaptDashboardData) is preserved. Only the data
 * source has changed from static JSON to live backend API responses.
 *
 * @module services/dashboardService
 */

import { getDashboardData } from '../api/dashboardApiService.js'
import { adaptDashboardData } from '../adapters/dashboardAdapter.js'

/**
 * Fetches and normalizes dashboard telemetry from the live FastAPI backend.
 *
 * Orchestrates parallel fetches from:
 *   - GET /api/v1/scans/
 *   - GET /api/v1/campaigns/
 *   - GET /api/v1/risk-scores/
 *   - GET /api/v1/health/ready
 *
 * @returns {Promise<import('../interfaces').DashboardData>}
 * @throws {import('../api/types').ApiError} On backend connection failure
 */
export async function getDashboard() {
  const raw = await getDashboardData()
  // Pass through adaptDashboardData to preserve the normalized shape
  // that all dashboard components depend on.
  return adaptDashboardData(raw)
}

export default { getDashboard }
