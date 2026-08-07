/**
 * Adapter to normalize raw threat intelligence and reporting responses.
 * 
 * @param {Object} raw Raw JSON or API response
 * @returns {import('../interfaces').ThreatFeedData} Normalized reports dataset
 */
export function adaptReportData(raw = {}) {
  const normalizedFeeds = {}
  if (raw.threatFeeds) {
    Object.keys(raw.threatFeeds).forEach((key) => {
      const feed = raw.threatFeeds[key] || {}
      normalizedFeeds[key] = {
        name: String(feed.name || ''),
        status: String(feed.status || 'Offline'),
        detectionRatio: feed.detectionRatio ? String(feed.detectionRatio) : undefined,
        reputation: feed.reputation !== undefined ? Number(feed.reputation) : undefined,
        lastAnalysis: feed.lastAnalysis ? String(feed.lastAnalysis) : undefined,
        communityScore: feed.communityScore !== undefined ? Number(feed.communityScore) : undefined,
        riskLevel: feed.riskLevel ? String(feed.riskLevel) : undefined,
        verifiedStatus: feed.verifiedStatus ? String(feed.verifiedStatus) : undefined,
        phishingReports: feed.phishingReports !== undefined ? Number(feed.phishingReports) : undefined,
        targetBrand: feed.targetBrand ? String(feed.targetBrand) : undefined,
        submissionDate: feed.submissionDate ? String(feed.submissionDate) : undefined,
        confidence: feed.confidence ? String(feed.confidence) : undefined,
        malwareFamily: feed.malwareFamily ? String(feed.malwareFamily) : undefined,
        threatCategory: feed.threatCategory ? String(feed.threatCategory) : undefined,
        urlStatus: feed.urlStatus ? String(feed.urlStatus) : undefined,
        hostStatus: feed.hostStatus ? String(feed.hostStatus) : undefined,
        tags: feed.tags ? feed.tags.map(String) : undefined,
        abuseConfidence: feed.abuseConfidence ? String(feed.abuseConfidence) : undefined,
        country: feed.country ? String(feed.country) : undefined,
        isp: feed.isp ? String(feed.isp) : undefined,
        usageType: feed.usageType ? String(feed.usageType) : undefined,
        reports: feed.reports !== undefined ? Number(feed.reports) : undefined,
        lastReported: feed.lastReported ? String(feed.lastReported) : undefined,
        error: feed.error ? String(feed.error) : undefined
      }
    })
  }

  return {
    threatFeeds: normalizedFeeds,
    iocs: (raw.iocs || []).map((ioc) => ({
      type: String(ioc.type || ''),
      value: String(ioc.value || ''),
      source: String(ioc.source || ''),
      severity: String(ioc.severity || 'low'),
      confidence: String(ioc.confidence || '0%'),
      status: String(ioc.status || 'Monitored')
    })),
    reputation: {
      verdict: String(raw.reputation?.verdict || 'Unknown'),
      riskLevel: String(raw.reputation?.riskLevel || 'Unknown'),
      score: Number(raw.reputation?.score || 0),
      maxScore: Number(raw.reputation?.maxScore || 100),
      confidence: String(raw.reputation?.confidence || '0%'),
      recommendation: String(raw.reputation?.recommendation || '')
    },
    recommendations: (raw.recommendations || []).map(String),
    reportPreview: {
      title: String(raw.reportPreview?.title || ''),
      executiveSummary: String(raw.reportPreview?.executiveSummary || ''),
      threatDescription: String(raw.reportPreview?.threatDescription || ''),
      riskAssessment: String(raw.reportPreview?.riskAssessment || ''),
      impact: String(raw.reportPreview?.impact || ''),
      timelineSummary: String(raw.reportPreview?.timelineSummary || ''),
      indicatorsSummary: String(raw.reportPreview?.indicatorsSummary || ''),
      analystNotes: String(raw.reportPreview?.analystNotes || ''),
      recommendations: String(raw.reportPreview?.recommendations || '')
    },
    exportOptions: (raw.exportOptions || []).map((opt) => ({
      id: String(opt.id || ''),
      name: String(opt.name || ''),
      desc: String(opt.desc || '')
    }))
  }
}

export default { adaptReportData }
