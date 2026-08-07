/**
 * Campaign Service — ThreatLens Frontend
 *
 * Stage A.5 — Campaigns Workspace API Integration.
 *
 * Queries CozyBear campaign details, infrastructure footprints, and timeline milestones.
 * Replaces mock services with live backend endpoints queries.
 *
 * @module services/campaignService
 */

import { getCampaignsList, getCampaignDetails } from '../api/campaignService.js'

/**
 * Retrieves the campaigns list or a single campaign's details.
 * Replaces the mock database read with a live API call to retrieve campaign
 * records and adapt them to the expected frontend interfaces.
 *
 * If no specific campaign ID is active, falls back to the first campaign found
 * in the active list, or returns null if no campaigns exist yet.
 *
 * @returns {Promise<import('../interfaces').CampaignData|null>}
 */
export async function getCampaigns() {
  const list = await getCampaignsList(0, 10)
  
  if (!list || list.length === 0) {
    return null
  }

  // Fetch the first campaign from the active list
  const activeCampaign = list[0]
  return getCampaignDetails(activeCampaign.campaign_id)
}

export default { getCampaigns }
