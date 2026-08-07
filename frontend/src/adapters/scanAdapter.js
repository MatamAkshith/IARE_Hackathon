/**
 * Adapter to normalize raw investigation check payloads.
 * 
 * @param {Object} raw Raw JSON or API response
 * @returns {import('../interfaces').InvestigationResult} Normalized target check results
 */
export function adaptScanData(raw = {}) {
  const normalizedEvidence = {}
  if (raw.evidence) {
    Object.keys(raw.evidence).forEach((key) => {
      normalizedEvidence[key] = (raw.evidence[key] || []).map((row) => ({
        label: String(row.label || ''),
        value: String(row.value || ''),
        mono: Boolean(row.mono),
        highlight: Boolean(row.highlight)
      }))
    })
  }

  return {
    url: String(raw.url || ''),
    risk: {
      score: Number(raw.risk?.score || 0),
      maxScore: Number(raw.risk?.maxScore || 100),
      level: String(raw.risk?.level || 'Unknown'),
      recommendation: String(raw.risk?.recommendation || ''),
      confidence: String(raw.risk?.confidence || '0%'),
      badgeColor: String(raw.risk?.badgeColor || '')
    },
    explanation: (raw.explanation || []).map(String),
    badges: (raw.badges || []).map((b) => ({
      label: String(b.label || ''),
      type: String(b.type || 'info')
    })),
    evidence: normalizedEvidence
  }
}

export default { adaptScanData }
