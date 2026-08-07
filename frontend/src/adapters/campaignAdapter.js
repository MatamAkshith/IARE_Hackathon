/**
 * Adapter to normalize raw campaign attribution responses.
 * 
 * @param {Object} raw Raw JSON or API response
 * @returns {import('../interfaces').CampaignData} Normalized campaign cluster dataset
 */
export function adaptCampaignData(raw = {}) {
  return {
    summary: {
      campaignName: String(raw.summary?.campaignName || ''),
      campaignId: String(raw.summary?.campaignId || ''),
      status: String(raw.summary?.status || ''),
      riskLevel: String(raw.summary?.riskLevel || 'Unknown'),
      confidence: String(raw.summary?.confidence || '0%'),
      firstSeen: String(raw.summary?.firstSeen || ''),
      lastSeen: String(raw.summary?.lastSeen || ''),
      totalDomains: Number(raw.summary?.totalDomains || 0),
      activeDomains: Number(raw.summary?.activeDomains || 0),
      infrastructureCount: Number(raw.summary?.infrastructureCount || 0),
      iocs: (raw.summary?.iocs || []).map(String)
    },
    connectedDomains: (raw.connectedDomains || []).map((dom) => ({
      id: Number(dom.id || 0),
      domain: String(dom.domain || ''),
      riskScore: Number(dom.riskScore || 0),
      status: String(dom.status || 'unknown'),
      firstSeen: String(dom.firstSeen || ''),
      lastSeen: String(dom.lastSeen || ''),
      country: String(dom.country || ''),
      hostingProvider: String(dom.hostingProvider || '')
    })),
    infrastructure: {
      ipAddress: String(raw.infrastructure?.ipAddress || ''),
      asn: String(raw.infrastructure?.asn || ''),
      hostingProvider: String(raw.infrastructure?.hostingProvider || ''),
      registrar: String(raw.infrastructure?.registrar || ''),
      nameservers: String(raw.infrastructure?.nameservers || ''),
      sslFingerprint: String(raw.infrastructure?.sslFingerprint || ''),
      whoisSimilarity: String(raw.infrastructure?.whoisSimilarity || '')
    },
    sharedEvidence: (raw.sharedEvidence || []).map((ev) => ({
      type: String(ev.type || ''),
      description: String(ev.description || ''),
      severity: String(ev.severity || 'low'),
      confidence: String(ev.confidence || '0%')
    })),
    confidence: {
      score: Number(raw.confidence?.score || 0),
      severity: String(raw.confidence?.severity || 'Unknown'),
      sharedIndicators: Number(raw.confidence?.sharedIndicators || 0),
      correlatedDomains: Number(raw.confidence?.correlatedDomains || 0),
      recommendation: String(raw.confidence?.recommendation || '')
    },
    timeline: (raw.timeline || []).map((item) => ({
      time: String(item.time || ''),
      title: String(item.title || ''),
      desc: String(item.desc || '')
    }))
  }
}

export default { adaptCampaignData }
