import React, { createContext, useState, useEffect } from 'react'
import { getDashboard } from '../services/dashboardService'
import { getCampaigns } from '../services/campaignService'
import { getReports } from '../services/reportService'

export const DataContext = createContext(null)

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
      setDashboard({ data: null, loading: false, error: err.message || 'Failed to load dashboard.' })
    }
  }

  const fetchCampaigns = async () => {
    setCampaigns((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const data = await getCampaigns()
      setCampaigns({ data, loading: false, error: null })
    } catch (err) {
      setCampaigns({ data: null, loading: false, error: err.message || 'Failed to load campaigns.' })
    }
  }

  const fetchReports = async () => {
    setReports((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const data = await getReports()
      setReports({ data, loading: false, error: null })
    } catch (err) {
      setReports({ data: null, loading: false, error: err.message || 'Failed to load threat reports.' })
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
