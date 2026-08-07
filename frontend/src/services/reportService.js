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
  const ext = details._raw?.external_evidence || {}
  const risk = details.risk

  const getProviderData = (name) => {
    const responses = ext.provider_responses || {};
    return responses[name] || ext[name] || {};
  };

  const vt = getProviderData('VirusTotal') || getProviderData('virustotal') || {};
  const pt = getProviderData('PhishTank') || getProviderData('phishtank') || {};
  const uh = getProviderData('URLHaus') || getProviderData('urlhaus') || {};
  const ab = getProviderData('AbuseIPDB') || getProviderData('abuseipdb') || {};

  const threatFeeds = {
    virustotal: {
      name: 'VirusTotal API',
      status: vt.status || (vt.error ? 'unavailable' : 'success'),
      detectionRatio: vt.raw_response?.data?.attributes?.last_analysis_stats
        ? `${vt.raw_response.data.attributes.last_analysis_stats.malicious || 0}/${(vt.raw_response.data.attributes.last_analysis_stats.malicious || 0) + (vt.raw_response.data.attributes.last_analysis_stats.harmless || 0) + (vt.raw_response.data.attributes.last_analysis_stats.undetected || 0)}`
        : (obs.virustotal_positives !== undefined ? `${obs.virustotal_positives}/${obs.virustotal_total || 90}` : '0/90'),
      reputation: vt.raw_response?.data?.attributes?.reputation !== undefined
        ? vt.raw_response.data.attributes.reputation
        : (obs.virustotal_reputation || 0),
      communityScore: vt.raw_response?.data?.attributes?.reputation !== undefined
        ? vt.raw_response.data.attributes.reputation
        : (obs.virustotal_reputation || 0),
      lastAnalysis: vt.raw_response?.data?.attributes?.last_analysis_date
        ? new Date(vt.raw_response.data.attributes.last_analysis_date * 1000).toISOString().split('T')[0]
        : (obs.whois_creation_date ? new Date(obs.whois_creation_date).toISOString().split('T')[0] : 'N/A'),
      error: vt.error || null,
      riskLevel: vt.verdict || (obs.virustotal_positives > 0 ? 'malicious' : 'clean')
    },
    phishtank: {
      name: 'PhishTank Database',
      status: pt.status || (pt.error ? 'unavailable' : 'success'),
      verifiedStatus: pt.verdict === 'malicious' ? 'Malicious ⚠' : (pt.verdict === 'clean' ? 'Clean' : 'Unknown'),
      phishingReports: pt.raw_response?.results?.phishing_reports || (pt.verdict === 'malicious' ? 1 : 0),
      targetBrand: pt.raw_response?.results?.target || 'Unknown',
      error: pt.error || null,
      confidence: pt.verdict === 'malicious' ? '100%' : 'N/A'
    },
    urlhaus: {
      name: 'URLHaus Feed',
      status: uh.status || (uh.error ? 'unavailable' : 'success'),
      urlStatus: uh.raw_response?.url_status || (uh.verdict === 'malicious' ? 'online' : 'offline'),
      threatCategory: uh.raw_response?.threat || 'N/A',
      tags: uh.raw_response?.tags || (obs.urlhaus_match ? ['phishing'] : []),
      error: uh.error || null
    },
    abuseipdb: {
      name: 'AbuseIPDB Connector',
      status: ab.status || (ab.error ? 'unavailable' : 'success'),
      abuseConfidence: ab.raw_response?.data?.abuseConfidenceScore !== undefined
        ? `${ab.raw_response.data.abuseConfidenceScore}%`
        : (obs.abuseipdb_score !== undefined ? `${obs.abuseipdb_score}%` : '0%'),
      country: ab.raw_response?.data?.countryCode || 'N/A',
      isp: ab.raw_response?.data?.isp || 'N/A',
      error: ab.error || null
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

/**
 * Fetches and adapts live threat intelligence feed data for a specific scan ID.
 * Accepts an explicit scan ID to load, without falling back to the latest.
 *
 * @param {number} scanId - The specific scan ID to load
 * @returns {Promise<import('../interfaces').ThreatFeedData|null>}
 */
export async function getReportForScan(scanId) {
  const details = await getInvestigationDetails(scanId)

  const obs = details._raw?.observations || {}
  const ext = details._raw?.external_evidence || {}
  const risk = details.risk

  const getProviderData = (name) => {
    const responses = ext.provider_responses || {};
    return responses[name] || ext[name] || {};
  };

  const vt = getProviderData('VirusTotal') || getProviderData('virustotal') || {};
  const pt = getProviderData('PhishTank') || getProviderData('phishtank') || {};
  const uh = getProviderData('URLHaus') || getProviderData('urlhaus') || {};
  const ab = getProviderData('AbuseIPDB') || getProviderData('abuseipdb') || {};

  const threatFeeds = {
    virustotal: {
      name: 'VirusTotal API',
      status: vt.status || (vt.error ? 'unavailable' : 'success'),
      detectionRatio: vt.raw_response?.data?.attributes?.last_analysis_stats
        ? `${vt.raw_response.data.attributes.last_analysis_stats.malicious || 0}/${(vt.raw_response.data.attributes.last_analysis_stats.malicious || 0) + (vt.raw_response.data.attributes.last_analysis_stats.harmless || 0) + (vt.raw_response.data.attributes.last_analysis_stats.undetected || 0)}`
        : (obs.virustotal_positives !== undefined ? `${obs.virustotal_positives}/${obs.virustotal_total || 90}` : '0/90'),
      reputation: vt.raw_response?.data?.attributes?.reputation !== undefined ? vt.raw_response.data.attributes.reputation : (obs.virustotal_reputation || 0),
      communityScore: vt.raw_response?.data?.attributes?.reputation !== undefined ? vt.raw_response.data.attributes.reputation : (obs.virustotal_reputation || 0),
      lastAnalysis: vt.raw_response?.data?.attributes?.last_analysis_date
        ? new Date(vt.raw_response.data.attributes.last_analysis_date * 1000).toISOString().split('T')[0]
        : (obs.whois_creation_date ? new Date(obs.whois_creation_date).toISOString().split('T')[0] : 'N/A'),
      error: vt.error || null,
      riskLevel: vt.verdict || (obs.virustotal_positives > 0 ? 'malicious' : 'clean')
    },
    phishtank: {
      name: 'PhishTank Database',
      status: pt.status || (pt.error ? 'unavailable' : 'success'),
      verifiedStatus: pt.verdict === 'malicious' ? 'Malicious ⚠' : (pt.verdict === 'clean' ? 'Clean' : 'Unknown'),
      phishingReports: pt.raw_response?.results?.phishing_reports || (pt.verdict === 'malicious' ? 1 : 0),
      targetBrand: pt.raw_response?.results?.target || 'Unknown',
      error: pt.error || null,
      confidence: pt.verdict === 'malicious' ? '100%' : 'N/A'
    },
    urlhaus: {
      name: 'URLHaus Feed',
      status: uh.status || (uh.error ? 'unavailable' : 'success'),
      urlStatus: uh.raw_response?.url_status || (uh.verdict === 'malicious' ? 'online' : 'offline'),
      threatCategory: uh.raw_response?.threat || 'N/A',
      tags: uh.raw_response?.tags || (obs.urlhaus_match ? ['phishing'] : []),
      error: uh.error || null
    },
    abuseipdb: {
      name: 'AbuseIPDB Connector',
      status: ab.status || (ab.error ? 'unavailable' : 'success'),
      abuseConfidence: ab.raw_response?.data?.abuseConfidenceScore !== undefined
        ? `${ab.raw_response.data.abuseConfidenceScore}%`
        : (obs.abuseipdb_score !== undefined ? `${obs.abuseipdb_score}%` : '0%'),
      country: ab.raw_response?.data?.countryCode || 'N/A',
      isp: ab.raw_response?.data?.isp || 'N/A',
      error: ab.error || null
    }
  }

  const iocs = []
  if (obs.ip_address) {
    iocs.push({ type: 'IP Address', value: obs.ip_address, source: 'DNS Resolution', severity: risk.score >= 80 ? 'critical' : risk.score >= 50 ? 'high' : 'medium', confidence: details.risk.confidence, status: 'active' })
  }
  if (obs.ssl_cert_serial) {
    iocs.push({ type: 'SSL Cert Serial', value: obs.ssl_cert_serial, source: 'TLS Handshake', severity: 'medium', confidence: 'high', status: 'active' })
  }
  ;(details.badges || []).forEach(b => {
    iocs.push({ type: 'Heuristic Flag', value: b.label, source: 'Risk Engine', severity: b.type === 'danger' ? 'high' : 'medium', confidence: 'high', status: 'active' })
  })

  const recommendations = details.explanation.map(exp => {
    if (exp.startsWith('Recommendation: ')) return exp.replace('Recommendation: ', '')
    return `Mitigate findings: ${exp}`
  })

  const reportPreview = {
    title: `INCIDENT REPORT: ${details.url.toUpperCase()}`,
    executiveSummary: details.aiSummary?.executive?.business_impact || `The target domain "${details.url}" was investigated and received a threat score of ${risk.score}/100.`,
    threatDescription: details.explanation.join('\n'),
    riskAssessment: `Risk Score: ${risk.score} / 100 • Verdict Severity: ${risk.level}`,
    impact: details.aiSummary?.executive?.recommended_action_summary || 'Escalate to Tier 2 SOC handler for firewall containment blocks.',
    timelineSummary: `Scan completed at: ${new Date(details.id).toISOString?.() || 'N/A'}`,
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

export default { getReports, getReportForScan }
