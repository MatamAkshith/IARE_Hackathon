/**
 * ThreatLens Core Data Model Interfaces (JSDoc Typedefs)
 */

/**
 * @typedef {Object} KPITrend
 * @property {string} value Trend percentage/change string (e.g. "+14%")
 * @property {boolean} positive Indicates if the trend is positive/favorable
 */

/**
 * @typedef {Object} KPICardItem
 * @property {string} id Unique card identifier (e.g. "total-scans")
 * @property {string} title Plain-text card label
 * @property {string} value Primary summary metric value
 * @property {KPITrend} [trend] Optional trend comparison detail
 * @property {string} type Color category (neutral, success, warning, danger, info)
 */

/**
 * @typedef {Object} ScanListItem
 * @property {number} id Unique scan record ID
 * @property {string} domain Inspected URL domain
 * @property {number|null} riskScore 0-100 calculated risk score
 * @property {string} status Progress state (completed, processing, failed)
 * @property {string} scanTime Timestamp logs
 * @property {string} campaign Attributed campaign cluster name
 */

/**
 * @typedef {Object} RiskDistributionItem
 * @property {string} label Range name (e.g. "Critical (90-100)")
 * @property {number} count Number of instances
 * @property {number} percentage Out of 100 percentage
 * @property {string} color Tailwind background CSS class
 */

/**
 * @typedef {Object} CampaignStatusItem
 * @property {string} label Progress group (e.g. "Active Monitoring")
 * @property {number} count Count of clusters
 * @property {string} color Tailwind text/bg border classes
 */

/**
 * @typedef {Object} ActivityLogItem
 * @property {string} time Event clock timestamp
 * @property {string} type Severity key (critical, high, medium, error, info)
 * @property {string} message Context log string
 */

/**
 * @typedef {Object} ThreatSummaryHighlight
 * @property {string} mostTargetedBrand Top targeted corporate identity
 * @property {string} mostCommonAttack Class vector category
 * @property {string} mostCommonTLD Dominant TLD string
 * @property {string} highestRiskDomain Max threat score target
 * @property {string} latestScan Last scanned domain
 */

/**
 * @typedef {Object} ServiceStatusItem
 * @property {string} name Ingestion engine label
 * @property {string} status State string (e.g. "Offline")
 * @property {string} color Tailwind dot background color
 */

/**
 * @typedef {Object} DashboardData
 * @property {KPICardItem[]} kpis KPI metrics card list
 * @property {ScanListItem[]} scans Ingested scans queue table
 * @property {RiskDistributionItem[]} riskDistribution Severity bands percentages
 * @property {CampaignStatusItem[]} campaigns Attributed cluster statistics
 * @property {ActivityLogItem[]} timeline Live events checkpoint log
 * @property {ThreatSummaryHighlight} threatSummary High risk summaries details
 * @property {ServiceStatusItem[]} services Registry component ready gauges
 */

/**
 * @typedef {Object} CampaignSummary
 * @property {string} campaignName Attributed cluster title
 * @property {string} campaignId Cluster reference ID
 * @property {string} status Monitoring state
 * @property {string} riskLevel Severity rating
 * @property {string} confidence Confidence percentage string
 * @property {string} firstSeen First registration timestamp
 * @property {string} lastSeen Latest activity timestamp
 * @property {number} totalDomains Total attributed domain count
 * @property {number} activeDomains Active monitoring count
 * @property {number} infrastructureCount Network nodes counts
 * @property {string[]} iocs Listed IP and hash signatures
 */

/**
 * @typedef {Object} CampaignDomainItem
 * @property {number} id Unique identifier
 * @property {string} domain Domain string
 * @property {number} riskScore Calculated threat score
 * @property {string} status Registration state
 * @property {string} firstSeen First detected time
 * @property {string} lastSeen Last scanned time
 * @property {string} country Host geographic country
 * @property {string} hostingProvider Hosting ISP company
 */

/**
 * @typedef {Object} SharedInfrastructure
 * @property {string} ipAddress Target resolution host IP
 * @property {string} asn Autonomous System Number label
 * @property {string} hostingProvider Ingestion provider
 * @property {string} registrar Registrant authority
 * @property {string} nameservers Assigned Nameservers
 * @property {string} sslFingerprint SHA-256 SSL footprint
 * @property {string} whoisSimilarity Registrar matching score
 */

/**
 * @typedef {Object} SharedEvidenceItem
 * @property {string} type Correlation parameter class (e.g. "HTML Similarity")
 * @property {string} description Findings descriptions details
 * @property {string} severity Level tag (high, medium, low)
 * @property {string} confidence Probability count percentage
 */

/**
 * @typedef {Object} CampaignConfidence
 * @property {number} score Attribution likelihood percentage
 * @property {string} severity Verdict severity indicator
 * @property {number} sharedIndicators Matches counts
 * @property {number} correlatedDomains Group size count
 * @property {string} recommendation Action summary text
 */

/**
 * @typedef {Object} CampaignTimelineItem
 * @property {string} time Action timestamp
 * @property {string} title Setup milestone checkpoint title
 * @property {string} desc Context details description
 */

/**
 * @typedef {Object} CampaignData
 * @property {CampaignSummary} summary Cluster outline
 * @property {CampaignDomainItem[]} connectedDomains Attribution domain list
 * @property {SharedInfrastructure} infrastructure Shared infrastructure details
 * @property {SharedEvidenceItem[]} sharedEvidence Core similarity criteria lists
 * @property {CampaignConfidence} confidence Final validation verdicts
 * @property {CampaignTimelineItem[]} timelineAttributions Step checkpoints history
 */

/**
 * @typedef {Object} ThreatFeedDetails
 * @property {string} name Third-party source title (e.g. "VirusTotal")
 * @property {string} status Connection ready state
 * @property {string} [detectionRatio] Flagged metrics
 * @property {number} [reputation] Score metrics
 * @property {string} [lastAnalysis] Timestamps
 * @property {number} [communityScore] Forum reviews
 * @property {string} [riskLevel] Severity level
 * @property {string} [verifiedStatus] verified status flags
 * @property {number} [phishingReports] reports counts
 * @property {string} [targetBrand] targeted company
 * @property {string} [submissionDate] dates
 * @property {string} [confidence] confidence percents
 * @property {string} [malwareFamily] malware group names
 * @property {string} [threatCategory] classification labels
 * @property {string} [urlStatus] domains status
 * @property {string} [hostStatus] server status
 * @property {string[]} [tags] query tags
 * @property {string} [abuseConfidence] abuse percentages
 * @property {string} [country] Geo-IP country
 * @property {string} [isp] Internet provider
 * @property {string} [usageType] Server class
 * @property {number} [reports] reports listings
 * @property {string} [lastReported] clock status
 */

/**
 * @typedef {Object} IOCRecordItem
 * @property {string} type Parameter type (Domain, SHA256)
 * @property {string} value Signature string
 * @property {string} source Detection database feed source
 * @property {string} severity Alert rating (critical, high, medium)
 * @property {string} confidence Verification probability percents
 * @property {string} status State tag
 */

/**
 * @typedef {Object} ReputationSummary
 * @property {string} verdict Verdict text ("Malicious")
 * @property {string} riskLevel Severity rating
 * @property {number} score Risk score out of 100
 * @property {number} maxScore Max score limits
 * @property {string} confidence Confidence percentage
 * @property {string} recommendation Action summary text
 */

/**
 * @typedef {Object} IncidentReport
 * @property {string} title Report draft reference header
 * @property {string} executiveSummary Summary text paragraphs
 * @property {string} threatDescription Vectors descriptions
 * @property {string} riskAssessment Score summaries
 * @property {string} impact Damage estimates
 * @property {string} timelineSummary Chronology log summary
 * @property {string} indicatorsSummary Attributions counts
 * @property {string} analystNotes Forensics logs notes
 * @property {string} recommendations Mitigation suggestions
 */

/**
 * @typedef {Object} ExportOptionItem
 * @property {string} id Format key (PDF, CSV)
 * @property {string} name Label button name
 * @property {string} desc Format specifications descriptions
 */

/**
 * @typedef {Object} ThreatFeedData
 * @property {Object.<string, ThreatFeedDetails>} threatFeeds Ingested sources cards
 * @property {IOCRecordItem[]} iocs Listed indicators details
 * @property {ReputationSummary} reputation Severity scores dial
 * @property {string[]} recommendations Firewall mitigation checklist
 * @property {IncidentReport} reportPreview Detailed incident description draft
 * @property {ExportOptionItem[]} exportOptions Disabled options buttons list
 */

/**
 * @typedef {Object} EvidenceRowItem
 * @property {string} label Telemetry metric key
 * @property {string} value Fetched evidence string
 * @property {boolean} [mono] Uses monospaced layout
 * @property {boolean} [highlight] Displays warning color
 */

/**
 * @typedef {Object} InvestigationResult
 * @property {string} url Target URL
 * @property {ReputationSummary} risk Score summary details
 * @property {string[]} explanation narratives bullet points
 * @property {Object[]} badges Alert tags
 * @property {Object.<string, EvidenceRowItem[]>} evidence DNS/WHOIS/SSL tables lists
 */
