import { useContext } from 'react'
import { DataContext } from '../providers/DataProvider'

/**
 * Custom hook to retrieve threat intelligence and reports.
 * 
 * @returns {{ reports: import('../interfaces').ThreatFeedData|null, loading: boolean, error: string|null, refetch: Function }}
 */
export default function useReports() {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useReports must be used within a DataProvider.')
  }
  return {
    reports: context.reports.data,
    loading: context.reports.loading,
    error: context.reports.error,
    refetch: context.reports.refetch
  }
}
