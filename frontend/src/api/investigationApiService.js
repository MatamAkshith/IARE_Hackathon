/**
 * Investigation API Service — ThreatLens Frontend
 *
 * Orchestrates the full URL investigation pipeline against the live FastAPI backend.
 *
 * The investigation pipeline executes these steps in sequence:
 *   1. POST /api/v1/domains/       → Create/register domain record → domain.id
 *   2. POST /api/v1/scans/         → Create scan record → scan.id
 *   3. POST /api/v1/extract/       → Run full extraction pipeline (WHOIS, DNS, TLS, HTML)
 *   4. POST /api/v1/unified-evidence/process  → Merge + normalize all evidence
 *   5. POST /api/v1/risk/evaluate  → Compute explainable risk score
 *   6. GET  /api/v1/unified-evidence/{indicator} → Retrieve evidence records
 *   7. GET  /api/v1/risk/{indicator}             → Retrieve risk assessment
 *   8. POST /api/v1/ai/report/analyst            → Generate AI analyst summary (optional)
 *   9. GET  /api/v1/campaigns/                   → Check campaign attribution
 *
 * The result is normalized into the InvestigationResult shape consumed by
 * adaptScanData() and the existing investigation components.
 *
 * @module api/investigationApiService
 */

import { apiClient } from './index.js'

// ── URL Validation ────────────────────────────────────────────────────────────

const URL_REGEX = /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/.*)?$/

/**
 * Validates that a string is a plausible URL or domain.
 *
 * @param {string} raw
 * @returns {{ valid: boolean, normalized: string, error: string|null }}
 */
export function validateAndNormalizeUrl(raw) {
  const trimmed = (raw || '').trim()
  if (!trimmed) {
    return { valid: false, normalized: '', error: 'Please enter a URL or domain to investigate.' }
  }
  if (!URL_REGEX.test(trimmed)) {
    return {
      valid: false,
      normalized: '',
      error: 'Invalid URL format. Enter a full URL (e.g. https://example.com) or bare domain.'
    }
  }
  // Ensure the indicator has a protocol for display purposes but also
  // pass the raw value as the indicator (backend normalizes internally)
  return { valid: true, normalized: trimmed, error: null }
}

// ── Step helpers ──────────────────────────────────────────────────────────────

/**
 * Step 1 & 2: Create domain + scan records and return scan.id.
 *
 * @param {string} url
 * @returns {Promise<{ domainId: number, scanId: number }>}
 */
async function createScanRecord(url) {
  const domain = await apiClient.post('/domains/', { url })
  const scan = await apiClient.post('/scans/', { domain_id: domain.id, status: 'pending' })
  return { domainId: domain.id, scanId: scan.id }
}

/**
 * Step 3: Run the full feature extraction pipeline.
 *
 * @param {string} url
 * @param {number} scanId
 * @returns {Promise<Object>} Raw extracted feature JSON
 */
async function runExtraction(url, scanId) {
  return apiClient.post('/extract/', { url, scan_id: scanId })
}

/**
 * Step 4: Process unified evidence (merge + normalize + score confidence).
 *
 * @param {string} indicator
 * @param {Object} extractedData
 * @returns {Promise<Object>} UnifiedEvidence object
 */
async function processEvidence(indicator, extractedData) {
  return apiClient.post('/unified-evidence/process', {
    indicator,
    internal_data: extractedData || {},
    external_data: {},
    save_to_db: true
  })
}

/**
 * Step 5: Run explainable risk evaluation.
 *
 * @param {string} indicator
 * @param {Object} evidence - The unified evidence payload from Step 4
 * @returns {Promise<Object>} RiskScore object
 */
async function evaluateRisk(indicator, evidence) {
  return apiClient.post('/risk/evaluate', {
    indicator,
    indicator_type: 'url',
    resolved_observations: evidence?.resolved_observations || {},
    save_to_db: true
  })
}

/**
 * Step 6: Retrieve persisted unified evidence records for indicator.
 *
 * @param {string} indicator
 * @returns {Promise<Array>} EvidenceRecordResponse list
 */
async function fetchEvidenceHistory(indicator) {
  return apiClient.get(`/unified-evidence/${encodeURIComponent(indicator)}`)
}

/**
 * Step 7: Retrieve persisted risk assessment history for indicator.
 *
 * @param {string} indicator
 * @returns {Promise<Array>} RiskAssessmentResponse list
 */
async function fetchRiskHistory(indicator) {
  return apiClient.get(`/risk/${encodeURIComponent(indicator)}`)
}

/**
 * Step 8: Request AI analyst report (optional — may fail gracefully).
 *
 * @param {string} indicator
 * @param {Object} evidence
 * @param {Object} riskAssessment
 * @returns {Promise<Object|null>}
 */
async function fetchAiReport(indicator, evidence, riskAssessment) {
  try {
    return await apiClient.post('/ai/report/analyst', {
      indicator,
      evidence: evidence || null,
      risk_assessment: riskAssessment || null,
      campaign_details: null
    })
  } catch {
    // AI report is supplementary — do not let its failure block the investigation
    return null
  }
}

/**
 * Step 9: Find any campaign that contains this indicator.
 *
 * @param {string} indicator
 * @param {Array} campaigns
 * @returns {Object|null} Matching campaign or null
 */
function findCampaignForIndicator(indicator, campaigns) {
  if (!Array.isArray(campaigns)) return null
  const lower = indicator.toLowerCase()
  return campaigns.find((c) => {
    return (c.members || []).some((m) =>
      (m.indicator || '').toLowerCase().includes(lower) ||
      lower.includes((m.indicator || '').toLowerCase())
    )
  }) || null
}

// ── Evidence normalizer ───────────────────────────────────────────────────────

import { getSeverityDetails } from '../utils/severityUtils'

/**
 * Maps a severity string to the badgeColor class expected by RiskSummary.
 *
 * @param {string} severity
 * @returns {string}
 */
function severityToStyle(severity) {
  return getSeverityDetails(severity).badgeClass
}


/**
 * Capitalizes first character of a string.
 *
 * @param {string} s
 * @returns {string}
 */
function capitalize(s) {
  if (!s) return ''
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase()
}

/**
 * Converts resolved_observations (flat JSON dict) into the EvidenceAccordion
 * section format: { domain: EvidenceRowItem[], dns: [], whois: [], ssl: [], html: [], metadata: [] }
 *
 * @param {Object} obs - resolved_observations from UnifiedEvidence
 * @returns {Object}
 */
function buildEvidenceSections(obs) {
  if (!obs || typeof obs !== 'object') return {}

  const ev = {
    domain: [],
    dns: [],
    whois: [],
    ssl: [],
    html: [],
    metadata: []
  }

  // ── Domain metadata ──────────────────────────────────────────────────────
  if (obs.domain || obs.registrar || obs.creation_date || obs.country_code) {
    const d = obs.domain_intelligence || obs
    const addIf = (label, val, opts = {}) => {
      if (val !== undefined && val !== null && val !== '') {
        ev.domain.push({ label, value: String(val), ...opts })
      }
    }
    addIf('Domain Name', d.domain || d.url || obs.indicator, { mono: true })
    addIf('Registrar Authority', d.registrar, { highlight: !d.registrar || d.registrar.toLowerCase().includes('redact') })
    addIf('Registration Date', d.creation_date, { highlight: true })
    addIf('Expiry Date', d.expiry_date)
    addIf('Hosting Country', d.country_code || d.country)
    addIf('Name Servers', Array.isArray(d.name_servers) ? d.name_servers.join(', ') : d.name_servers, { mono: true })
  }

  // ── DNS records ──────────────────────────────────────────────────────────
  if (obs.dns_records || obs.a_records || obs.ip_address) {
    const d = obs.network_intelligence || obs
    const dns = obs.dns_records || {}
    const addIf = (label, val, opts = {}) => {
      if (val !== undefined && val !== null && val !== '') {
        ev.dns.push({ label, value: String(val), ...opts })
      }
    }
    addIf('A Record (IP)', d.ip_address || (Array.isArray(dns.A) ? dns.A.join(', ') : dns.A), { mono: true })
    addIf('MX Records', Array.isArray(dns.MX) ? dns.MX.join(', ') : dns.MX, { mono: true })
    addIf('NS Records', Array.isArray(dns.NS) ? dns.NS.join(', ') : dns.NS, { mono: true })
    addIf('ASN', d.asn, { mono: true })
    addIf('Hosting Provider', d.hosting_provider || d.isp)
  }

  // ── WHOIS ────────────────────────────────────────────────────────────────
  if (obs.whois_data || obs.registrar || obs.creation_date) {
    const w = obs.whois_data || obs.domain_intelligence || obs
    const addIf = (label, val, opts = {}) => {
      if (val !== undefined && val !== null && val !== '') {
        ev.whois.push({ label, value: String(val), ...opts })
      }
    }
    addIf('WHOIS Registrar', w.registrar, { mono: true })
    addIf('Creation Timestamp', w.creation_date)
    addIf('Registry Expiration', w.expiry_date)
    addIf('Registrant Identity', w.registrant_name || w.registrant || 'Privacy Protected', {
      highlight: !w.registrant_name
    })
    addIf('Domain Age', w.domain_age || w.age)
  }

  // ── TLS / SSL ────────────────────────────────────────────────────────────
  if (obs.tls_data || obs.ssl_cert || obs.common_name || obs.issuer) {
    const t = obs.tls_intelligence || obs.tls_data || obs
    const addIf = (label, val, opts = {}) => {
      if (val !== undefined && val !== null && val !== '') {
        ev.ssl.push({ label, value: String(val), ...opts })
      }
    }
    addIf('Certificate Common Name', t.common_name, { mono: true })
    addIf('Certificate Issuer', t.issuer, {
      highlight: !t.issuer || t.issuer.toLowerCase().includes('self') || t.issuer.toLowerCase().includes('unknown')
    })
    addIf('Valid From', t.valid_from)
    addIf('Valid Until', t.valid_to || t.expiry, {
      highlight: t.is_expired || false
    })
    addIf('SANs', Array.isArray(t.san_list) ? t.san_list.join(', ') : t.san_list, { mono: true })
  }

  // ── HTML / webpage metrics ───────────────────────────────────────────────
  if (obs.html_data || obs.page_title !== undefined || obs.form_count !== undefined) {
    const h = obs.webpage_intelligence || obs.html_data || obs
    const addIf = (label, val, opts = {}) => {
      if (val !== undefined && val !== null && val !== '') {
        ev.html.push({ label, value: String(val), ...opts })
      }
    }
    addIf('Page Title', h.page_title)
    addIf('Form Count', h.form_count !== undefined ? String(h.form_count) : undefined)
    addIf('Has Password Field', h.has_password_field !== undefined ? (h.has_password_field ? 'Yes ⚠' : 'No') : undefined, {
      highlight: h.has_password_field === true
    })
    addIf('External Links', h.external_links !== undefined ? String(h.external_links) : undefined)
    addIf('Resource Count', h.resource_count !== undefined ? String(h.resource_count) : undefined)
  }

  // ── HTTP metadata / threat intel ─────────────────────────────────────────
  if (obs.threat_intel || obs.virustotal || obs.phishtank) {
    const ti = obs.threat_intel || obs
    const addIf = (label, val, opts = {}) => {
      if (val !== undefined && val !== null && val !== '') {
        ev.metadata.push({ label, value: String(val), ...opts })
      }
    }
    const vt = ti.virustotal || {}
    addIf('VirusTotal Detections', vt.detection_ratio || vt.detections, {
      highlight: !!(vt.detection_ratio || vt.detections), mono: true
    })
    const pt = ti.phishtank || {}
    addIf('PhishTank Status', pt.is_phishing !== undefined
      ? (pt.is_phishing ? 'Confirmed Phishing ⚠' : 'Clean')
      : pt.status, { highlight: pt.is_phishing === true })
    const uh = ti.urlhaus || {}
    addIf('URLHaus Status', uh.url_status || uh.status, {
      highlight: uh.url_status === 'online' || uh.status === 'online'
    })
    const ab = ti.abuseipdb || {}
    addIf('AbuseIPDB Confidence', ab.abuse_confidence_score !== undefined
      ? `${ab.abuse_confidence_score}%`
      : ab.abuse_confidence, { mono: true })
  }

  // Strip empty sections
  Object.keys(ev).forEach((k) => {
    if (ev[k].length === 0) {
      ev[k] = [{ label: 'Status', value: 'No data gathered for this category.' }]
    }
  })

  return ev
}

/**
 * Builds the badge list from a risk score object.
 *
 * @param {Object} riskRecord - RiskAssessmentResponse from backend
 * @returns {{ label: string, type: string }[]}
 */
function buildBadges(riskRecord) {
  const badges = []
  const severity = (riskRecord?.severity || '').toLowerCase()
  if (severity === 'critical') badges.push({ label: 'Critical Risk', type: 'danger' })
  else if (severity === 'high') badges.push({ label: 'High Risk', type: 'danger' })
  else if (severity === 'medium') badges.push({ label: 'Medium Risk', type: 'warning' })

  const breakdown = riskRecord?.breakdown || {}
  if (breakdown.new_domain) badges.push({ label: 'New Domain', type: 'danger' })
  if (breakdown.self_signed_ssl || breakdown.ssl_issues) badges.push({ label: 'SSL Issues', type: 'danger' })
  if (breakdown.phishing_form || breakdown.credential_harvesting) badges.push({ label: 'Credential Harvesting', type: 'danger' })
  if (breakdown.brand_impersonation) badges.push({ label: 'Brand Impersonation', type: 'warning' })
  if (breakdown.suspicious_tld) badges.push({ label: 'Suspicious TLD', type: 'warning' })
  if (breakdown.recently_registered) badges.push({ label: 'Recently Registered', type: 'info' })

  if (badges.length === 0 && severity) {
    badges.push({ label: capitalize(severity) + ' Severity', type: severity === 'low' ? 'info' : 'warning' })
  }
  return badges
}

/**
 * Extracts explanation bullet points from a risk record.
 *
 * @param {Object} riskRecord
 * @returns {string[]}
 */
function buildExplanation(riskRecord) {
  if (!riskRecord) return ['No explanation available — risk scoring may not have completed.']

  const lines = []
  const explanation = riskRecord.explanation
  if (typeof explanation === 'string' && explanation.trim()) {
    // Single string: split by newlines or sentences
    lines.push(...explanation.split('\n').map((s) => s.trim()).filter(Boolean))
  } else if (Array.isArray(explanation)) {
    lines.push(...explanation.filter(Boolean).map(String))
  }

  const recs = riskRecord.recommendations
  if (Array.isArray(recs) && recs.length > 0) {
    recs.forEach((r) => {
      const text = typeof r === 'string' ? r : r?.description || r?.text
      if (text) lines.push(`Recommendation: ${text}`)
    })
  }

  return lines.length > 0 ? lines : ['Risk scoring completed — no detailed explanation returned.']
}

// ── Main exported function ────────────────────────────────────────────────────

/**
 * Executes the full investigation pipeline for a URL and assembles the result
 * into the InvestigationResult shape consumed by adaptScanData().
 *
 * @param {string} url - The raw URL string to investigate
 * @returns {Promise<import('../interfaces').InvestigationResult>}
 * @throws {import('./types').ApiError} On unrecoverable pipeline failure
 */
export async function runInvestigation(url) {
  // ── Step 1+2: Register domain + scan ──────────────────────────────────────
  let scanId
  try {
    const record = await createScanRecord(url)
    scanId = record.scanId
  } catch (err) {
    throw err // Domain/scan creation failure is unrecoverable
  }

  // ── Step 3: Feature extraction (may be slow — 5-15s for real domains) ──
  let extractedData = {}
  try {
    extractedData = await runExtraction(url, scanId)
  } catch {
    // Extraction failure is non-fatal — proceed with empty internal_data
    extractedData = {}
  }

  // ── Step 4: Process unified evidence ──────────────────────────────────────
  let unifiedEvidence = null
  try {
    unifiedEvidence = await processEvidence(url, extractedData)
  } catch {
    unifiedEvidence = null
  }

  // ── Step 5: Risk evaluation ───────────────────────────────────────────────
  let riskScore = null
  try {
    riskScore = await evaluateRisk(url, unifiedEvidence)
  } catch {
    riskScore = null
  }

  // ── Step 6+7: Retrieve persisted records in parallel ─────────────────────
  const [evidenceResult, riskHistoryResult] = await Promise.allSettled([
    fetchEvidenceHistory(url),
    fetchRiskHistory(url)
  ])

  const evidenceRecords = evidenceResult.status === 'fulfilled' ? (evidenceResult.value || []) : []
  const riskRecords = riskHistoryResult.status === 'fulfilled' ? (riskHistoryResult.value || []) : []

  // Use the most recent record from each
  const latestEvidence = evidenceRecords[0] || null
  const latestRisk = riskRecords[0] || riskScore

  // ── Step 8: AI Analyst Report (optional) ─────────────────────────────────
  const aiReport = await fetchAiReport(url, latestEvidence, latestRisk)

  // ── Assemble InvestigationResult ─────────────────────────────────────────
  const obs = latestEvidence?.resolved_observations || unifiedEvidence?.resolved_observations || {}
  const score = latestRisk?.overall_score ?? riskScore?.overall_score ?? 0
  const severity = latestRisk?.severity ?? riskScore?.severity ?? 'unknown'

  return {
    url,
    risk: {
      score: Math.round(score),
      maxScore: 100,
      level: capitalize(severity),
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
      confidence: latestRisk?.indicator_type
        ? (latestEvidence?.overall_confidence || 'medium')
        : (latestEvidence?.overall_confidence || 'medium'),
      badgeColor: severityToStyle(severity)
    },
    explanation: buildExplanation(latestRisk),
    badges: buildBadges(latestRisk),
    evidence: buildEvidenceSections(obs),
    // Extended fields available for future components
    _raw: {
      scanId,
      evidenceRecord: latestEvidence,
      riskRecord: latestRisk,
      aiReport,
      observations: obs
    }
  }
}

/**
 * Retrieves the scan submission history (list of scans with domain info).
 *
 * @returns {Promise<Array>} Raw ScanResponse list from backend
 */
export async function getInvestigationHistory() {
  return apiClient.get('/scans/', { params: { skip: 0, limit: 50 } })
}

export default { runInvestigation, validateAndNormalizeUrl, getInvestigationHistory }
