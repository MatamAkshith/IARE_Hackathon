/**
 * Report Service — ThreatLens Frontend
 *
 * Stage A.5 — Reports Workspace API Integration.
 *
 * Replaces mock threat intelligence data with live backend observations.
 * Fetches the latest completed scan, queries its unified evidence and risk details,
 * and normalizes the payload.
 *
 * @module services/reportService
 */

import { getInvestigationHistory, getInvestigationDetails } from '../api/investigationService.js'
import { adaptReportData } from '../adapters/reportAdapter.js'

/**
 * Fetches and adapts live threat intelligence feed data for the Reports page.
 * Loads the most recent completed scan, and maps its evidence observations.
 *
 * If no scans exist, returns a zero-state payload to prevent crashing.
 *
 * @returns {Promise<import('../interfaces').ThreatFeedData|null>}
 */
export async function getReports() {
  const history = await getInvestigationHistory()
  const completedScans = (history || []).filter(s => s.status === 'completed')

  if (completedScans.length === 0) {
    // Zero-state default structure
    return adaptReportData({
      threatFeeds: {
        virustotal: { name: 'VirusTotal', status: 'Inactive', verdict: 'No data' },
        phishtank: { name: 'PhishTank', status: 'Inactive', verdict: 'No data' },
        urlhaus: { name: 'URLHaus', status: 'Inactive', verdict: 'No data' },
        abuseipdb: { name: 'AbuseIPDB', status: 'Inactive', verdict: 'No data' }
      },
      iocs: [],
      reputation: { verdict: 'Unknown', riskLevel: 'low', score: 0, maxScore: 100, confidence: '0%', recommendation: 'No scans run.' },
      recommendations: [],
      reportPreview: { title: 'Incident Report Preview', executiveSummary: 'No active threat target has been scanned yet.' },
      exportOptions: [{ id: 'MD', name: 'Markdown (.md)', desc: 'Export evidence details' }]
    })
  }

  // Fetch the latest scan's details
  const latestScan = completedScans[0]
  const details = await getInvestigationDetails(latestScan.id)

  const obs = details._raw?.observations || {}
  const risk = details.risk

  // Build external threat feeds connector statuses
  const vt = obs.virustotal || {}
  const pt = obs.phishtank || {}
  const uh = obs.urlhaus || {}
  const ab = obs.abuseipdb || {}

  const threatFeeds = {
    virustotal: {
      name: 'VirusTotal API',
      status: vt.status || 'Active',
      detectionRatio: vt.detection_ratio || '0/90',
      communityScore: vt.community_score || 0,
      lastAnalysis: vt.last_analysis_date || 'N/A'
    },
    phishtank: {
      name: 'PhishTank Database',
      status: pt.status || 'Active',
      verifiedStatus: pt.is_phishing ? 'Malicious ⚠' : 'Clean',
      phishingReports: pt.reports_count || 0,
      targetBrand: pt.target || 'Unknown'
    },
    urlhaus: {
      name: 'URLHaus Feed',
      status: uh.status || 'Active',
      urlStatus: uh.url_status || 'offline',
      threatCategory: uh.threat || 'N/A',
      tags: uh.tags || []
    },
    abuseipdb: {
      name: 'AbuseIPDB Connector',
      status: ab.status || 'Active',
      abuseConfidence: ab.abuse_confidence_score !== undefined ? `${ab.abuse_confidence_score}%` : '0%',
      country: ab.country_code || 'N/A',
      isp: ab.isp || 'N/A'
    }
  }

  // Build IOC list
  const iocs = []
  if (obs.ip_address) {
    iocs.push({
      type: 'IP Address',
      value: obs.ip_address,
      source: 'DNS Resolution',
      severity: risk.score >= 80 ? 'critical' : risk.score >= 50 ? 'high' : 'medium',
      confidence: details.risk.confidence,
      status: 'active'
    })
  }
  if (obs.ssl_cert_serial) {
    iocs.push({
      type: 'SSL Cert Serial',
      value: obs.ssl_cert_serial,
      source: 'TLS Handshake',
      severity: 'medium',
      confidence: 'high',
      status: 'active'
    })
  }
  (details.badges || []).forEach(b => {
    iocs.push({
      type: 'Heuristic Flag',
      value: b.label,
      source: 'Risk Engine',
      severity: b.type === 'danger' ? 'high' : 'medium',
      confidence: 'high',
      status: 'active'
    })
  })

  // Recommendations checklist
  const recommendations = details.explanation.map(exp => {
    if (exp.startsWith('Recommendation: ')) return exp.replace('Recommendation: ', '')
    return `Mitigate findings: ${exp}`
  })

  // Incident report preview
  const reportPreview = {
    title: `INCIDENT REPORT: ${details.url.toUpperCase()}`,
    executiveSummary: details.aiSummary?.executive?.business_impact || `The target domain "${details.url}" was investigated and received a threat score of ${risk.score}/100.`,
    threatDescription: details.explanation.join('\n'),
    riskAssessment: `Risk Score: ${risk.score} / 100 • Verdict Severity: ${risk.level}`,
    impact: details.aiSummary?.executive?.recommended_action_summary || 'Esclate to Tier 2 SOC handler for firewall containment blocks.',
    timelineSummary: `Scan completed at: ${latestScan.scanTime}`,
    indicatorsSummary: `${iocs.length} related IOCs mapped.`,
    analystNotes: details.aiSummary?.analyst?.conclusion || 'No supplementary analyst logs compiled.',
    recommendations: recommendations.join('\n')
  }

  return adaptReportData({
    threatFeeds,
    iocs,
    reputation: {
      verdict: risk.level,
      riskLevel: risk.level.toLowerCase(),
      score: risk.score,
      maxScore: 100,
      confidence: risk.confidence,
      recommendation: risk.recommendation
    },
    recommendations,
    reportPreview,
    exportOptions: [
      { id: 'MD', name: 'Markdown (.md)', desc: 'Export incident overview' },
      { id: 'JSON', name: 'JSON Report (.json)', desc: 'Full pipeline payload export' }
    ]
  })
}

export default { getReports }
