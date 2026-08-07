import { useContext } from 'react'
import { DataContext } from '../providers/DataProvider'

/**
 * Custom hook to retrieve dashboard statistics.
 * 
 * @returns {{ dashboard: import('../interfaces').DashboardData|null, loading: boolean, error: string|null, refetch: Function }}
 */
export default function useDashboard() {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useDashboard must be used within a DataProvider.')
  }
  return {
    dashboard: context.dashboard.data,
    loading: context.dashboard.loading,
    error: context.dashboard.error,
    refetch: context.dashboard.refetch
  }
}
