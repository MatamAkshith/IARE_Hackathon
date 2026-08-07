/**
 * Investigation API Service — ThreatLens Frontend
 *
 * Stage A.3 & Stage A.4: Centralized API layer for URL submission, scan progress polling,
 * scan history, and retrieving detailed unified investigation telemetry (Evidence, Threat Intel,
 * Risk Scoring, Campaigns, and AI reports).
 *
 * Consists of four core interfaces:
 *   - submitInvestigation(url)
 *   - getInvestigationStatus(id)
 *   - getInvestigationHistory()
 *   - getInvestigationDetails(id)
 *
 * @module api/investigationService
 */

import { apiClient } from './index.js'
import { validateAndNormalizeUrl } from './investigationApiService.js'

// Cache of running background pipelines in this browser tab/session
// to keep track of active tasks and coordinate client-driven execution.
const activePipelines = new Map()

/**
 * Triggers the 5-step analysis pipeline in the background on the server,
 * updating the scan record status along the way.
 *
 * @param {string} url
 * @param {number} scanId
 */
async function runBackgroundAnalysis(url, scanId) {
  try {
    // 1. Update status to 'scanning'
    await apiClient.put(`/scans/${scanId}`, { status: 'scanning' })

    // 2. Extract features
    const extractedData = await apiClient.post('/extract/', { url, scan_id: scanId })

    // 3. Process unified evidence
    const unifiedEvidence = await apiClient.post('/unified-evidence/process', {
      indicator: url,
      internal_data: extractedData || {},
      external_data: {},
      save_to_db: true
    })

    // 4. Evaluate explainable risk
    await apiClient.post('/risk/evaluate', {
      indicator: url,
      indicator_type: 'url',
      resolved_observations: unifiedEvidence?.resolved_observations || {},
      save_to_db: true
    })

    // 5. Correlate with campaigns (optional - fails gracefully)
    try {
      await apiClient.post('/campaigns/correlate', {
        indicator: url,
        indicator_type: 'url',
        ip_address: unifiedEvidence?.resolved_observations?.ip_address || '',
        cert_serial: unifiedEvidence?.resolved_observations?.ssl_cert_serial || '',
        page_title: unifiedEvidence?.resolved_observations?.page_title || ''
      })
    } catch (e) {
      console.warn('[Background Analysis] Campaign correlation failed:', e)
    }

    // 6. Generate AI analyst summary report in background (optional - fails gracefully)
    try {
      await apiClient.post('/ai/report/analyst', {
        indicator: url,
        evidence: unifiedEvidence || null,
        risk_assessment: null,
        campaign_details: null
      })
    } catch (e) {
      console.warn('[Background Analysis] AI report pre-generation failed:', e)
    }

    // 7. Update status to 'completed'
    await apiClient.put(`/scans/${scanId}`, { status: 'completed' })
  } catch (err) {
    console.error('[Background Analysis] Pipeline failed for scan ID:', scanId, err)
    try {
      await apiClient.put(`/scans/${scanId}`, { status: 'failed' })
    } catch (e) {
      console.error('[Background Analysis] Could not update failed scan status:', e)
    }
  } finally {
    activePipelines.delete(scanId)
  }
}

/**
 * Submits a new URL target for deep threat investigation.
 * Registers the domain, creates a new scan in the DB with status 'pending',
 * and kicks off the extraction pipeline in the background.
 *
 * @param {string} url - Target URL or bare domain
 * @returns {Promise<Object>} The registered ScanResponse record
 */
export async function submitInvestigation(url) {
  // Validate URL format first
  const { valid, normalized, error } = validateAndNormalizeUrl(url)
  if (!valid) {
    const validationError = new Error(error)
    validationError.code = 'VALIDATION_ERROR'
    throw validationError
  }

  // 1. Create domain record (or retrieve if existing)
  const domain = await apiClient.post('/domains/', { url: normalized })

  // 2. Create scan record with status 'pending'
  const scan = await apiClient.post('/scans/', {
    domain_id: domain.id,
    status: 'pending'
  })

  // 3. Kick off async pipeline task in background (do not await)
  const pipelinePromise = runBackgroundAnalysis(normalized, scan.id)
  activePipelines.set(scan.id, pipelinePromise)

  // Attach url to scan response for convenience
  return { ...scan, url: normalized }
}

/**
 * Retrieves the current status of an active scan by its ID.
 * Primarily used by the frontend polling loops during analysis.
 *
 * @param {number} id - Scan record ID
 * @returns {Promise<Object>} Scan status data (id, status, url)
 */
export async function getInvestigationStatus(id) {
  const scan = await apiClient.get(`/scans/${id}`)
  
  // Resolve domain name for display if available
  let url = ''
  try {
    const domain = await apiClient.get(`/domains/${scan.domain_id}`)
    url = domain.url
  } catch {
    url = `Scan #${scan.id}`
  }

  return {
    id: scan.id,
    status: scan.status || 'unknown',
    url
  }
}

/**
 * Retrieves the history of all submitted investigations.
 * Returns a list of scans populated with domain URLs.
 *
 * @returns {Promise<Array>} List of scan records with URLs
 */
export async function getInvestigationHistory() {
  const [scans, domains] = await Promise.all([
    apiClient.get('/scans/', { params: { skip: 0, limit: 100 } }),
    apiClient.get('/domains/', { params: { skip: 0, limit: 100 } })
  ])

  const domainMap = {}
  domains.forEach(d => {
    domainMap[d.id] = d.url
  })

  return scans.map(s => ({
    id: s.id,
    domain: domainMap[s.domain_id] || `Scan #${s.id}`,
    status: s.status || 'unknown',
    scanTime: new Date(s.created_at).toISOString().replace('T', ' ').substring(0, 16),
    campaign_id: s.campaign_id
  }))
}

/**
 * Retrieves full unified details for a completed investigation.
 * Builds evidence tables, risk score breakdowns, related campaigns, and AI reports.
 *
 * @param {number} id - Completed scan ID
 * @returns {Promise<Object>} Detailed telemetry payload for InvestigationDetails
 */
export async function getInvestigationDetails(id) {
  // 1. Fetch scan
  const scan = await apiClient.get(`/scans/${id}`)
  
  // 2. Fetch domain url
  const domain = await apiClient.get(`/domains/${scan.domain_id}`)
  const url = domain.url

  // 3. Parallel fetch of evidence and risk records
  const [evidenceHistory, riskHistory, campaigns] = await Promise.all([
    apiClient.get(`/unified-evidence/${encodeURIComponent(url)}`).catch(() => []),
    apiClient.get(`/risk/${encodeURIComponent(url)}`).catch(() => []),
    apiClient.get('/campaigns/').catch(() => [])
  ])

  // Get latest records
  const latestEvidence = evidenceHistory[0] || null
  const latestRisk = riskHistory[0] || null

  // 4. Generate AI summaries using current database values
  let aiReport = null
  let aiExecutive = null
  try {
    const reportReq = {
      indicator: url,
      evidence: latestEvidence || null,
      risk_assessment: latestRisk || null,
      campaign_details: null
    }
    
    const [analystRes, execRes] = await Promise.all([
      apiClient.post('/ai/report/analyst', reportReq).catch(() => null),
      apiClient.post('/ai/report/executive', reportReq).catch(() => null)
    ])
    aiReport = analystRes
    aiExecutive = execRes
  } catch (err) {
    console.warn('[Details Service] AI reports generation failed:', err)
  }

  // 5. Campaign context
  const correlatedCampaign = findCampaignForIndicator(url, campaigns)

  // 6. Map everything to structured component data format
  const obs = latestEvidence?.resolved_observations || {}
  const score = latestRisk?.overall_score ?? 0
  const severity = latestRisk?.severity ?? 'low'

  return {
    id: scan.id,
    url,
    status: scan.status,
    risk: {
      score: Math.round(score),
      maxScore: 100,
      level: severity.charAt(0).toUpperCase() + severity.slice(1).toLowerCase(),
      recommendation: (() => {
        const recs = latestRisk?.recommendations
        if (Array.isArray(recs) && recs.length > 0) {
          const first = recs[0]
          return typeof first === 'string' ? first : first?.description || first?.text || 'Review and monitor.'
        }
        if (score >= 80) return 'Block immediately and escalate.'
        if (score >= 50) return 'Quarantine and review.'
        return 'Monitor for future activity.'
      })(),
      confidence: latestEvidence?.overall_confidence || 'medium',
      badgeColor: severity === 'critical'
        ? 'bg-rose-950/20 text-rose-400 border-rose-800/40 shadow-rose-500/10'
        : severity === 'high'
        ? 'bg-amber-950/20 text-amber-400 border-amber-800/40 shadow-amber-500/5'
        : 'bg-emerald-950/20 text-emerald-400 border-emerald-800/40'
    },
    explanation: latestRisk?.explanation
      ? (typeof latestRisk.explanation === 'string'
          ? latestRisk.explanation.split('\n').map(s => s.trim()).filter(Boolean)
          : Array.isArray(latestRisk.explanation)
          ? latestRisk.explanation.map(String)
          : [])
      : ['No explainable risk scoring detail logged.'],
    badges: (() => {
      const b = []
      if (severity === 'critical' || severity === 'high') b.push({ label: `${severity.toUpperCase()} RISK`, type: 'danger' })
      const bd = latestRisk?.breakdown || {}
      if (bd.brand_impersonation) b.push({ label: 'Impersonation', type: 'danger' })
      if (bd.credential_harvesting) b.push({ label: 'Phish Forms', type: 'danger' })
      if (bd.new_domain) b.push({ label: 'New Domain', type: 'warning' })
      if (bd.ssl_issues) b.push({ label: 'SSL Issues', type: 'warning' })
      return b.length > 0 ? b : [{ label: 'Monitored', type: 'info' }]
    })(),
    evidence: buildEvidenceSections(obs),
    campaign: correlatedCampaign ? {
      id: correlatedCampaign.campaign_id,
      name: correlatedCampaign.name,
      severity: correlatedCampaign.severity,
      members: correlatedCampaign.members || []
    } : null,
    aiSummary: {
      analyst: aiReport,
      executive: aiExecutive
    },
    _raw: { observations: obs, external_evidence: latestEvidence?.external_evidence || {} }
  }
}

/** Helper: Find campaign containing target indicator */
function findCampaignForIndicator(indicator, campaigns) {
  if (!Array.isArray(campaigns)) return null
  const lower = indicator.toLowerCase()
  return campaigns.find(c =>
    (c.members || []).some(m =>
      (m.indicator || '').toLowerCase().includes(lower) ||
      lower.includes((m.indicator || '').toLowerCase())
    )
  ) || null
}

/** Helper: Map observations JSON to evidence category tables */
function buildEvidenceSections(obs) {
  const ev = {
    domain: [],
    dns: [],
    whois: [],
    ssl: [],
    html: [],
    metadata: []
  }

  const add = (section, label, val, opts = {}) => {
    if (val !== undefined && val !== null && val !== '') {
      ev[section].push({ label, value: String(val), ...opts })
    }
  }

  // Domain Metadata
  add('domain', 'Domain Name', obs.domain_name || obs.url || obs.indicator, { mono: true })
  add('domain', 'Registrar', obs.whois_registrar)
  add('domain', 'Created Date', obs.whois_creation_date, { highlight: true })
  add('domain', 'TLD Suffix', obs.tld, { mono: true })

  // DNS
  add('dns', 'IP Address', obs.ip_address, { mono: true })
  add('dns', 'Reverse PTR', obs.reverse_dns, { mono: true })
  add('dns', 'Hosting Provider', obs.hosting_provider)

  // WHOIS
  add('whois', 'WHOIS Server', obs.whois_server)
  add('whois', 'Expiration Date', obs.whois_expiration_date)
  add('whois', 'Registrant Name', obs.registrant_name || 'Redacted / Private', { highlight: !obs.registrant_name })

  // SSL/TLS
  add('ssl', 'Common Name', obs.ssl_common_name, { mono: true })
  add('ssl', 'Issuer', obs.ssl_issuer, { highlight: (obs.ssl_issuer || '').toLowerCase().includes('fake') })
  add('ssl', 'Expiration Days', obs.ssl_days_remaining !== undefined ? `${obs.ssl_days_remaining} days` : null)

  // HTML
  add('html', 'Page Title', obs.page_title)
  add('html', 'Password Field Count', obs.password_fields_count, { highlight: (obs.password_fields_count || 0) > 0 })
  add('html', 'Total Form Tags', obs.forms_count)
  add('html', 'Suspicious Keywords', obs.suspicious_keywords_found ? 'Found ⚠' : 'None', { highlight: obs.suspicious_keywords_found })

  // Metadata/Feeds
  add('metadata', 'HTTP Status', obs.http_status_code)
  add('metadata', 'Server header', obs.server_header, { mono: true })
  add('metadata', 'VirusTotal Ratio', obs.virustotal_positives !== undefined ? `${obs.virustotal_positives}/${obs.virustotal_total}` : null, { highlight: (obs.virustotal_positives || 0) > 0 })
  add('metadata', 'URLHaus Match', obs.urlhaus_match ? 'Listed ⚠' : 'Clean', { highlight: obs.urlhaus_match })

  // Clean empty sections
  Object.keys(ev).forEach(k => {
    if (ev[k].length === 0) {
      ev[k].push({ label: 'Status', value: 'No telemetry collected in this category.' })
    }
  })

  return ev
}
