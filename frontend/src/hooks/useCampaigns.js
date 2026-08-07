import { useContext } from 'react'
import { DataContext } from '../providers/DataProvider'

/**
 * Custom hook to retrieve CozyBear campaigns correlation.
 * 
 * @returns {{ campaigns: import('../interfaces').CampaignData|null, loading: boolean, error: string|null, refetch: Function }}
 */
export default function useCampaigns() {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useCampaigns must be used within a DataProvider.')
  }
  return {
    campaigns: context.campaigns.data,
    loading: context.campaigns.loading,
    error: context.campaigns.error,
    refetch: context.campaigns.refetch
  }
}
