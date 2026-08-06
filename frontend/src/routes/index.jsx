import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '../layouts/DashboardLayout'
import Dashboard from '../pages/Dashboard'
import Investigation from '../pages/Investigation'
import Campaigns from '../pages/Campaigns'
import Reports from '../pages/Reports'
import Settings from '../pages/Settings'

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        {/* Redirect empty paths to the primary Dashboard panel */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/scans" element={<Investigation />} />
        <Route path="/campaigns" element={<Campaigns />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
        {/* Wildcard redirect back to home */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  )
}
