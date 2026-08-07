/**
 * DataProvider — ThreatLens Frontend
 *
 * **Stage A.2**: Updated error handling to extract structured `ApiError` messages
 * from the centralized error handler. The `fetchDashboard` function now uses the
 * live `getDashboard()` from `src/services/dashboardService.js` which calls the
 * real backend API.
 *
 * Data fetching strategy: Context + useEffect on mount with manual refetch support.
 * All three resource groups (dashboard, campaigns, reports) are loaded in parallel
 * on application startup.
 */

import React, { createContext, useState, useEffect } from 'react'
import { getDashboard } from '../services/dashboardService'
import { getCampaigns } from '../services/campaignService'
import { getReports } from '../services/reportService'
import { isApiError } from '../api/index.js'

export const DataContext = createContext(null)

/**
 * Extracts a human-readable error message from any thrown error value.
 * Handles structured ApiError objects and plain Error instances.
 *
 * @param {unknown} err - The caught error value
 * @param {string} fallback - Default message if extraction fails
 * @returns {string}
 */
function extractErrorMessage(err, fallback) {
  if (isApiError(err)) return err.message
  if (err instanceof Error) return err.message
  if (typeof err === 'string') return err
  return fallback
}

export function DataProvider({ children }) {
  const [dashboard, setDashboard] = useState({ data: null, loading: true, error: null })
  const [campaigns, setCampaigns] = useState({ data: null, loading: true, error: null })
  const [reports, setReports] = useState({ data: null, loading: true, error: null })

  const fetchDashboard = async () => {
    setDashboard((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const data = await getDashboard()
      setDashboard({ data, loading: false, error: null })
    } catch (err) {
      setDashboard({
        data: null,
        loading: false,
        error: extractErrorMessage(err, 'Unable to reach the ThreatLens backend. Is the server running?')
      })
    }
  }

  const fetchCampaigns = async () => {
    setCampaigns((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const data = await getCampaigns()
      setCampaigns({ data, loading: false, error: null })
    } catch (err) {
      setCampaigns({
        data: null,
        loading: false,
        error: extractErrorMessage(err, 'Failed to load campaign attribution data.')
      })
    }
  }

  const fetchReports = async () => {
    setReports((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const data = await getReports()
      setReports({ data, loading: false, error: null })
    } catch (err) {
      setReports({
        data: null,
        loading: false,
        error: extractErrorMessage(err, 'Failed to load threat intelligence reports.')
      })
    }
  }

  // Load all telemetry on mount
  useEffect(() => {
    fetchDashboard()
    fetchCampaigns()
    fetchReports()
  }, [])

  const value = {
    dashboard: {
      ...dashboard,
      refetch: fetchDashboard
    },
    campaigns: {
      ...campaigns,
      refetch: fetchCampaigns
    },
    reports: {
      ...reports,
      refetch: fetchReports
    }
  }

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  )
}
