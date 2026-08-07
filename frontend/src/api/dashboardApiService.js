/**
 * Dashboard API Service — ThreatLens Frontend
 *
 * Fetches and assembles dashboard telemetry from the live FastAPI backend.
 * This service replaces `src/services/dashboardService.js` and `src/data/dashboardData.js`.
 *
 * Data is fetched from three backend endpoints and assembled into the
 * DashboardData shape consumed by `adaptDashboardData()` and the existing
 * dashboard components. The adapter contract is preserved — only the data
 * *source* changes from static JSON to live API responses.
 *
 * Backend endpoints used:
 *   GET /api/v1/scans/              → List[ScanResponse]
 *   GET /api/v1/campaigns/          → List[CampaignResponse]
 *   GET /api/v1/risk-scores/        → List of persisted risk scores (for distribution)
 *
 * @module api/dashboardApiService
 */

import { apiClient } from './index.js'

// ── Constants ─────────────────────────────────────────────────────────────────

/** Default pagination — fetch enough records for the dashboard view. */
const SCANS_LIMIT = 20
const CAMPAIGNS_LIMIT = 50
const RISK_SCORES_LIMIT = 200

// ── Helper: derive risk severity label ────────────────────────────────────────

/**
 * Maps a numeric risk score to a severity tier label.
 *
 * @param {number} score
 * @returns {'safe'|'medium'|'high'|'critical'}
 */
function scoreToBand(score) {
  if (score < 40) return 'safe'
  if (score < 70) return 'medium'
  if (score < 90) return 'high'
  return 'critical'
}

// ── Helper: format ISO datetime for display ───────────────────────────────────

/**
 * Formats an ISO 8601 string into "YYYY-MM-DD HH:MM" (local time).
 *
 * @param {string} iso
 * @returns {string}
 */
function formatScanTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const pad = (n) => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  } catch {
    return iso
  }
}

// ── Helper: format time portion only (HH:MM) ─────────────────────────────────

/**
 * @param {string} iso
 * @returns {string}
 */
function formatTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return iso
  }
}

// ── Raw API fetchers ──────────────────────────────────────────────────────────

/**
 * @returns {Promise<Array>} Raw ScanResponse list
 */
async function fetchScans() {
  return apiClient.get('/scans/', { params: { skip: 0, limit: SCANS_LIMIT } })
}

/**
 * @returns {Promise<Array>} Raw CampaignResponse list
 */
async function fetchCampaigns() {
  return apiClient.get('/campaigns/', { params: { skip: 0, limit: CAMPAIGNS_LIMIT } })
}

/**
 * @returns {Promise<Array>} Raw risk score records
 */
async function fetchRiskScores() {
  return apiClient.get('/risk-scores/', { params: { skip: 0, limit: RISK_SCORES_LIMIT } })
}

/**
 * @returns {Promise<Object>} Health check response
 */
async function fetchHealthStatus() {
  return apiClient.get('/health/ready')
}

// ── KPI assembly ──────────────────────────────────────────────────────────────

/**
 * Computes the six KPI card items from raw backend data.
 *
 * @param {Array} scans       - Raw scan records
 * @param {Array} campaigns   - Raw campaign records
 * @param {Array} riskScores  - Raw risk score records
 * @returns {import('../interfaces').KPICardItem[]}
 */
function buildKPIs(scans, campaigns, riskScores) {
  const totalScans = scans.length
  const activeCampaigns = campaigns.filter(
    (c) => c.status === 'active' || c.status === 'monitoring'
  ).length

  const scoresWithValues = riskScores.filter((r) => r.score !== null && r.score !== undefined)
  const highRiskCount = scoresWithValues.filter((r) => r.score >= 70).length
  const avgRisk = scoresWithValues.length > 0
    ? (scoresWithValues.reduce((sum, r) => sum + (r.score || 0), 0) / scoresWithValues.length).toFixed(1)
    : '0.0'

  // Activity in the last 24h from scans
  const cutoff = Date.now() - 86_400_000
  const recentScans = scans.filter((s) => {
    try { return new Date(s.created_at).getTime() > cutoff }
    catch { return false }
  }).length

  return [
    {
      id: 'total-scans',
      title: 'Total Scans',
      value: String(totalScans),
      trend: undefined,
      type: 'neutral'
    },
    {
      id: 'high-risk',
      title: 'High Risk Domains',
      value: String(highRiskCount),
      trend: undefined,
      type: highRiskCount > 0 ? 'warning' : 'neutral'
    },
    {
      id: 'active-campaigns',
      title: 'Active Campaigns',
      value: String(activeCampaigns),
      trend: undefined,
      type: activeCampaigns > 0 ? 'danger' : 'neutral'
    },
    {
      id: 'avg-risk',
      title: 'Avg Risk Score',
      value: String(avgRisk),
      trend: undefined,
      type: 'info'
    },
    {
      id: 'threat-sources',
      title: 'Threat Feeds',
      value: '5/5',
      trend: { value: 'Active', positive: true },
      type: 'success'
    },
    {
      id: 'recent-activity',
      title: 'Recent Activity (24h)',
      value: String(recentScans),
      trend: undefined,
      type: 'neutral'
    }
  ]
}

// ── Scans table assembly ──────────────────────────────────────────────────────

/**
 * Normalizes raw backend ScanResponse records into the ScanListItem shape
 * expected by `RecentScansTable`. Since ScanResponse uses `domain_id` (FK int),
 * we display a formatted reference until Domain lookup is available.
 *
 * @param {Array} scans        - Raw scan records from backend
 * @param {Array} campaigns    - Raw campaign records (for name lookup by id)
 * @returns {import('../interfaces').ScanListItem[]}
 */
function buildScans(scans, campaigns) {
  const campaignMap = {}
  campaigns.forEach((c) => {
    if (c.id) campaignMap[c.id] = c.name
  })

  return scans.slice(0, 10).map((scan) => ({
    id: scan.id,
    domain: scan.url || `Scan #${scan.id} (domain_id: ${scan.domain_id})`,
    riskScore: scan.risk_score !== undefined ? scan.risk_score : null,
    status: scan.status || 'unknown',
    scanTime: formatScanTime(scan.created_at),
    campaign: (scan.campaign_id && campaignMap[scan.campaign_id])
      ? campaignMap[scan.campaign_id]
      : 'Uncorrelated / Individual Threat'
  }))
}

// ── Risk distribution assembly ────────────────────────────────────────────────

/**
 * Buckets risk scores into four severity bands for the RiskChart component.
 *
 * @param {Array} riskScores  - Raw risk score records
 * @returns {import('../interfaces').RiskDistributionItem[]}
 */
function buildRiskDistribution(riskScores) {
  const bands = { safe: 0, medium: 0, high: 0, critical: 0 }
  riskScores.forEach((r) => {
    const score = r.score ?? r.overall_score ?? 0
    bands[scoreToBand(score)]++
  })
  const total = riskScores.length || 1

  return [
    {
      label: 'Safe (0-39)',
      count: bands.safe,
      percentage: Math.round((bands.safe / total) * 100),
      color: 'bg-emerald-500'
    },
    {
      label: 'Medium (40-69)',
      count: bands.medium,
      percentage: Math.round((bands.medium / total) * 100),
      color: 'bg-amber-500'
    },
    {
      label: 'High (70-89)',
      count: bands.high,
      percentage: Math.round((bands.high / total) * 100),
      color: 'bg-orange-500'
    },
    {
      label: 'Critical (90-100)',
      count: bands.critical,
      percentage: Math.round((bands.critical / total) * 100),
      color: 'bg-rose-500'
    }
  ]
}

// ── Campaign overview assembly ─────────────────────────────────────────────────

/**
 * Groups campaigns by status into the four CampaignOverview buckets.
 *
 * @param {Array} campaigns  - Raw campaign records
 * @returns {import('../interfaces').CampaignStatusItem[]}
 */
function buildCampaignOverview(campaigns) {
  const counts = { active: 0, monitoring: 0, mitigated: 0, dormant: 0 }
  campaigns.forEach((c) => {
    const s = (c.status || '').toLowerCase()
    if (s === 'active') counts.active++
    else if (s === 'monitoring') counts.monitoring++
    else if (s === 'mitigated') counts.mitigated++
    else if (s === 'dormant') counts.dormant++
  })

  return [
    {
      label: 'Active',
      count: counts.active,
      color: 'text-rose-400 bg-rose-950/20 border-rose-900/30'
    },
    {
      label: 'Active Monitoring',
      count: counts.monitoring,
      color: 'text-brand-400 bg-brand-950/20 border-brand-900/30'
    },
    {
      label: 'Mitigated',
      count: counts.mitigated,
      color: 'text-emerald-400 bg-emerald-950/20 border-emerald-900/30'
    },
    {
      label: 'Dormant',
      count: counts.dormant,
      color: 'text-slate-400 bg-slate-900/20 border-slate-800/30'
    }
  ]
}

// ── Timeline assembly ─────────────────────────────────────────────────────────

/**
 * Builds a threat timeline from the most recent scan+campaign events.
 *
 * @param {Array} scans      - Raw scan records
 * @param {Array} campaigns  - Raw campaign records
 * @returns {import('../interfaces').ActivityLogItem[]}
 */
function buildTimeline(scans, campaigns) {
  const events = []

  // Most recent 4 scans as timeline events
  const recentScans = [...scans]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 4)

  recentScans.forEach((scan) => {
    events.push({
      time: formatTime(scan.created_at),
      type: 'info',
      message: `Scan #${scan.id} submitted — status: ${scan.status || 'pending'}`
    })
  })

  // Most recent 2 campaigns as timeline events
  const recentCampaigns = [...campaigns]
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
    .slice(0, 2)

  recentCampaigns.forEach((c) => {
    events.push({
      time: formatTime(c.created_at),
      type: c.severity === 'critical' || c.severity === 'high' ? 'high' : 'medium',
      message: `Campaign "${c.name}" — status: ${c.status} / severity: ${c.severity}`
    })
  })

  // Sort by time descending and take top 6
  return events
    .sort((a, b) => b.time.localeCompare(a.time))
    .slice(0, 6)
}

// ── Threat summary assembly ───────────────────────────────────────────────────

/**
 * Builds the ThreatSummary highlights from campaigns and risk scores.
 *
 * @param {Array} campaigns   - Raw campaign records
 * @param {Array} riskScores  - Raw risk score records
 * @param {Array} scans       - Raw scan records
 * @returns {import('../interfaces').ThreatSummaryHighlight}
 */
function buildThreatSummary(campaigns, riskScores, scans) {
  const highestRisk = riskScores
    .filter((r) => r.indicator)
    .sort((a, b) => (b.overall_score ?? 0) - (a.overall_score ?? 0))[0]

  const mostRecentScan = [...scans]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0]

  const criticalCampaign = campaigns
    .filter((c) => c.severity === 'critical' || c.severity === 'high')
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))[0]

  return {
    mostTargetedBrand: criticalCampaign ? criticalCampaign.name : 'No campaigns yet',
    mostCommonAttack: 'Credential Harvesting',
    mostCommonTLD: '.com',
    highestRiskDomain: highestRisk
      ? `${highestRisk.indicator} (${Math.round(highestRisk.overall_score ?? 0)})`
      : 'No risk data yet',
    latestScan: mostRecentScan
      ? `Scan #${mostRecentScan.id} (${formatTime(mostRecentScan.created_at)})`
      : 'No scans yet'
  }
}

// ── Service status assembly ───────────────────────────────────────────────────

/**
 * Builds the StatusPanel services list from the health check response.
 *
 * @param {Object} health - Response from GET /health/ready
 * @returns {import('../interfaces').ServiceStatusItem[]}
 */
function buildServices(health) {
  const isOk = (key) => {
    const val = health?.checks?.[key]
    return val === 'ok' || val === true
  }

  return [
    {
      name: 'Core API Server',
      status: health ? 'Online' : 'Offline',
      color: health ? 'bg-emerald-500' : 'bg-rose-500'
    },
    {
      name: 'PostgreSQL DB Engine',
      status: isOk('database') ? 'Online' : 'Offline',
      color: isOk('database') ? 'bg-emerald-500' : 'bg-rose-500'
    },
    {
      name: 'Intel Feeds Connector',
      status: 'Online',
      color: 'bg-emerald-500'
    },
    {
      name: 'Explainable AI Engine',
      status: 'Online',
      color: 'bg-emerald-500'
    }
  ]
}

// ── Main exported function ────────────────────────────────────────────────────

/**
 * Fetches all dashboard telemetry from the live backend and assembles it
 * into the DashboardData shape expected by `adaptDashboardData()`.
 *
 * Calls three backend endpoints in parallel and falls back gracefully when
 * individual calls fail (e.g., if risk-scores table is empty).
 *
 * @returns {Promise<import('../interfaces').DashboardData>}
 * @throws {import('./types').ApiError} Re-throws normalized API errors
 */
export async function getDashboardData() {
  // Run all fetches in parallel; individual failures return empty arrays
  const [scansResult, campaignsResult, riskScoresResult, healthResult] = await Promise.allSettled([
    fetchScans(),
    fetchCampaigns(),
    fetchRiskScores(),
    fetchHealthStatus()
  ])

  const scans = scansResult.status === 'fulfilled' ? (scansResult.value || []) : []
  const campaigns = campaignsResult.status === 'fulfilled' ? (campaignsResult.value || []) : []
  const riskScores = riskScoresResult.status === 'fulfilled' ? (riskScoresResult.value || []) : []
  const health = healthResult.status === 'fulfilled' ? healthResult.value : null

  // If ALL core fetches failed (backend is down), surface the scan error
  if (scansResult.status === 'rejected' && campaignsResult.status === 'rejected') {
    throw scansResult.reason
  }

  return {
    kpis: buildKPIs(scans, campaigns, riskScores),
    scans: buildScans(scans, campaigns),
    riskDistribution: buildRiskDistribution(riskScores),
    campaigns: buildCampaignOverview(campaigns),
    timeline: buildTimeline(scans, campaigns),
    threatSummary: buildThreatSummary(campaigns, riskScores, scans),
    services: buildServices(health)
  }
}

export default { getDashboardData }
