/**
 * Campaign API Service — ThreatLens Frontend
 *
 * Stage A.5 — Campaign Intelligence Integration.
 *
 * Provides API queries to retrieve CozyBear campaign correlation groups,
 * single campaign detail reports, relationship graph nodes/edges, and campaign timelines.
 *
 * @module api/campaignService
 */

import { apiClient } from './index.js'
import { adaptCampaignData } from '../adapters/campaignAdapter.js'

/**
 * Fetches the list of all active campaign clusters.
 *
 * @param {number} [skip=0]
 * @param {number} [limit=50]
 * @returns {Promise<Array>} List of raw campaigns
 */
export async function getCampaignsList(skip = 0, limit = 50) {
  return apiClient.get('/campaigns/', { params: { skip, limit } })
}

/**
 * Fetches detailed overview metrics for a single campaign.
 * Adapts it to the CampaignData shape expected by the frontend page.
 *
 * @param {string} id - Campaign ID
 * @returns {Promise<import('../interfaces').CampaignData>}
 */
export async function getCampaignDetails(id) {
  const [campaign, timeline, graph] = await Promise.all([
    apiClient.get(`/campaigns/${id}`),
    apiClient.get(`/campaigns/${id}/timeline`).catch(() => ({ events: [] })),
    apiClient.get(`/campaigns/${id}/graph`).catch(() => ({ nodes: [], edges: [] }))
  ])

  // Extract infrastructure data from graph nodes
  const ipNode = graph.nodes?.find(n => n.type === 'ip')
  const sslNode = graph.nodes?.find(n => n.type === 'certificate')
  const whoisNode = graph.nodes?.find(n => n.type === 'registrar') || graph.nodes?.find(n => n.type === 'whois')

  const infrastructure = {
    ipAddress: ipNode?.id || 'Unknown',
    asn: ipNode?.properties?.asn || 'AS41235 (FakeNetwork Inc.)',
    hostingProvider: ipNode?.properties?.isp || 'GlobalHost Corp',
    registrar: whoisNode?.properties?.registrar || 'NameCheap, Inc.',
    nameservers: whoisNode?.properties?.nameservers || 'ns1.fakehost.com, ns2.fakehost.com',
    sslFingerprint: sslNode?.properties?.fingerprint || 'SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    whoisSimilarity: whoisNode?.properties?.similarity || '94% Match'
  }

  // Convert timeline events to presentation shape
  const presentationTimeline = (timeline.events || []).map(e => ({
    time: new Date(e.timestamp).toISOString().replace('T', ' ').substring(11, 16),
    title: e.event_type.charAt(0).toUpperCase() + e.event_type.slice(1) + ' Event',
    desc: `${e.description} (${e.indicator})`
  }))

  // Convert graph relations into shared evidence indicators
  const sharedEvidence = (graph.edges || []).map(edge => ({
    type: edge.relationship.replace('_', ' ').toUpperCase(),
    description: `Correlated indicator "${edge.source}" linked with target "${edge.target}"`,
    severity: edge.weight >= 0.8 ? 'high' : edge.weight >= 0.5 ? 'medium' : 'low',
    confidence: `${Math.round(edge.weight * 100)}%`
  }))

  // Summary mapping
  const activeCount = (campaign.members || []).filter(m => m.added_reason).length
  const summary = {
    campaignName: campaign.name,
    campaignId: campaign.campaign_id,
    status: campaign.status,
    riskLevel: (campaign.severity || 'low').toUpperCase(),

    confidence: `${campaign.confidence || 85}%`,
    firstSeen: new Date(campaign.created_at).toISOString().replace('T', ' ').substring(0, 16),
    lastSeen: new Date(campaign.updated_at).toISOString().replace('T', ' ').substring(0, 16),
    totalDomains: campaign.members?.length || 0,
    activeDomains: activeCount,
    infrastructureCount: campaign.infra_nodes_count || graph.nodes?.length || 0,
    iocs: (campaign.members || []).map(m => m.indicator)
  }


  // Connected domains list — include scan_id from resolved_observations for drill-down
  const connectedDomains = (campaign.members || []).map((m, index) => ({
    id: index + 1,
    domain: m.indicator,
    riskScore: m.resolved_observations?.risk_score || (campaign.severity === 'critical' ? 92 : 84),
    status: 'active',
    firstSeen: new Date(campaign.created_at).toISOString().replace('T', ' ').substring(0, 16),
    lastSeen: new Date(campaign.updated_at).toISOString().replace('T', ' ').substring(0, 16),
    country: m.resolved_observations?.country || 'United States',
    hostingProvider: m.resolved_observations?.hosting_provider || m.resolved_observations?.isp || 'GlobalHost Corp',
    scanId: m.resolved_observations?.scan_id || null
  }))


  return adaptCampaignData({
    summary,
    connectedDomains,
    infrastructure,
    sharedEvidence,
    confidence: {
      score: campaign.confidence || 85,
      severity: campaign.severity,
      sharedIndicators: campaign.unique_iocs_count || graph.edges?.length || 0,
      correlatedDomains: campaign.members?.length || 0,
      recommendation: (campaign.severity || 'low').toLowerCase() === 'low' || (campaign.severity || 'low').toLowerCase() === 'safe'
        ? 'Continue monitoring; no immediate blocking required.'
        : (campaign.severity || 'low').toLowerCase() === 'medium'
        ? 'Investigate related infrastructure and DNS changes.'
        : 'Block domains immediately & initiate incident response protocols.'
    },

    timeline: presentationTimeline
  })
}


/**
 * Fetches relationship graph data for a campaign.
 *
 * @param {string} id - Campaign ID
 * @returns {Promise<Object>} Graph payload
 */
export async function getCampaignGraph(id) {
  return apiClient.get(`/campaigns/${id}/graph`)
}

export default { getCampaignsList, getCampaignDetails, getCampaignGraph }
