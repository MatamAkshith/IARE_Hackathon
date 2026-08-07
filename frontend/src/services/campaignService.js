import { delay } from './mockApi'
import { campaignData } from '../data/campaignData'
import { adaptCampaignData } from '../adapters/campaignAdapter'

/**
 * Service to retrieve CozyBear campaign correlation groups.
 * 
 * @returns {Promise<CampaignData>}
 */
export async function getCampaigns() {
  await delay(400, 700)
  
  if (sessionStorage.getItem('mock_campaign_error') === 'true') {
    throw new Error('Failed to retrieve attributed campaign clusters.')
  }
  
  return adaptCampaignData(campaignData)
}

export default { getCampaigns }
