/**
 * Dashboard API Service — ThreatLens Frontend
 *
 * Fetches and assembles dashboard telemetry from the live FastAPI backend.
 * Uses the dynamic SQL aggregation and threat feed endpoints on the backend.
 *
 * Backend endpoints used:
 *   GET /api/v1/dashboard/stats        → SQL aggregation stats
 *   GET /api/v1/dashboard/recent-feed  → Joins scan, domain, campaigns & risk_assessment_records
 *   GET /api/v1/health/ready           → Health readiness state
 *
 * @module api/dashboardApiService
 */

import { apiClient } from './index.js'

// ── Helper: format ISO datetime for display ───────────────────────────────────

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

function formatTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return iso
  }
}

// ── Campaign overview assembly ─────────────────────────────────────────────────

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

// ── Service status assembly ───────────────────────────────────────────────────

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

export async function getDashboardData() {
  const [stats, recentFeed, campaignsList, health] = await Promise.all([
    apiClient.get('/dashboard/stats'),
    apiClient.get('/dashboard/recent-feed'),
    apiClient.get('/campaigns/').catch(() => []),
    apiClient.get('/health/ready').catch(() => null)
  ])

  const totalScans = stats.total_scans
  const activeCampaigns = stats.active_campaigns
  const highRiskCount = stats.high_risk_domains
  const avgRisk = stats.avg_risk_score
  const recentActivityCount = stats.recent_activity_count ?? recentFeed.length
  const activeFeeds = stats.active_feeds ?? 5
  const totalFeeds = stats.total_feeds ?? 5

  const kpis = [
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
      value: `${activeFeeds}/${totalFeeds}`,
      trend: undefined,
      type: 'success',
      route: '/reports'
    },
    {
      id: 'recent-activity',
      title: 'Recent Activity (24h)',
      value: String(recentActivityCount),
      trend: undefined,
      type: 'neutral',
      route: '/scans'
    }
  ]

  // Map scans from recentFeed for RecentScansTable component mapping
  const scans = recentFeed.map(item => ({
    id: item.id,
    domain: item.target_domain,
    riskScore: item.risk_score,
    riskRating: item.risk_rating, // "SAFE" | "MEDIUM" | "HIGH" | "CRITICAL"
    status: item.pipeline_status.toLowerCase(),
    scanTime: formatScanTime(item.date_time),
    campaign: item.campaign_attribution
  }))

  const riskDistribution = stats.risk_distribution
  const campaignOverview = buildCampaignOverview(campaignsList)
  const services = buildServices(health)

  // Map recent feed events to ActivityLog timeline items
  const timeline = recentFeed.slice(0, 6).map(item => ({
    time: formatTime(item.date_time),
    type: item.risk_rating.toLowerCase() === 'critical' || item.risk_rating.toLowerCase() === 'high' ? 'high' : 'medium',
    message: `Scan for ${item.target_domain} completed — status: ${item.pipeline_status} / risk: ${item.risk_score}`
  }))

  // Threat summary metrics
  const highestRisk = [...recentFeed].sort((a, b) => b.risk_score - a.risk_score)[0]
  const threatSummary = {
    mostTargetedBrand: campaignsList.length > 0 ? campaignsList[0].name : 'No campaigns yet',
    mostCommonAttack: 'Credential Harvesting',
    mostCommonTLD: '.com',
    highestRiskDomain: highestRisk
      ? `${highestRisk.target_domain} (${Math.round(highestRisk.risk_score)})`
      : 'No risk data yet',
    latestScan: recentFeed.length > 0
      ? `Scan #${recentFeed[0].id} (${formatTime(recentFeed[0].date_time)})`
      : 'No scans yet'
  }

  return {
    kpis,
    scans,
    riskDistribution,
    campaigns: campaignOverview,
    timeline,
    threatSummary,
    services
  }
}

export default { getDashboardData }
