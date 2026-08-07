/**
 * Adapter to normalize raw dashboard payloads.
 * 
 * @param {Object} raw Raw JSON or API response
 * @returns {import('../interfaces').DashboardData} Normalized dashboard dataset
 */
export function adaptDashboardData(raw = {}) {
  return {
    kpis: (raw.kpis || []).map((kpi) => ({
      id: String(kpi.id || ''),
      title: String(kpi.title || ''),
      value: String(kpi.value || '0'),
      trend: kpi.trend ? {
        value: String(kpi.trend.value || ''),
        positive: Boolean(kpi.trend.positive)
      } : undefined,
      type: String(kpi.type || 'neutral'),
      route: kpi.route ? String(kpi.route) : undefined
    })),
    scans: (raw.scans || []).map((scan) => ({
      id: Number(scan.id || 0),
      domain: String(scan.domain || ''),
      riskScore: scan.riskScore !== null && scan.riskScore !== undefined ? Number(scan.riskScore) : null,
      status: String(scan.status || 'unknown'),
      scanTime: String(scan.scanTime || ''),
      campaign: String(scan.campaign || 'Uncorrelated / Individual Threat')
    })),
    riskDistribution: (raw.riskDistribution || []).map((item) => ({
      label: String(item.label || ''),
      count: Number(item.count || 0),
      percentage: Number(item.percentage || 0),
      color: String(item.color || 'bg-slate-500')
    })),
    campaigns: (raw.campaigns || []).map((c) => ({
      label: String(c.label || ''),
      count: Number(c.count || 0),
      color: String(c.color || '')
    })),
    timeline: (raw.timeline || []).map((evt) => ({
      time: String(evt.time || ''),
      type: String(evt.type || 'info'),
      message: String(evt.message || '')
    })),
    threatSummary: {
      mostTargetedBrand: String(raw.threatSummary?.mostTargetedBrand || ''),
      mostCommonAttack: String(raw.threatSummary?.mostCommonAttack || ''),
      mostCommonTLD: String(raw.threatSummary?.mostCommonTLD || ''),
      highestRiskDomain: String(raw.threatSummary?.highestRiskDomain || ''),
      latestScan: String(raw.threatSummary?.latestScan || '')
    },
    services: (raw.services || []).map((srv) => ({
      name: String(srv.name || ''),
      status: String(srv.status || 'Offline'),
      color: String(srv.color || 'bg-rose-500')
    }))
  }
}

export default { adaptDashboardData }
