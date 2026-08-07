import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '../layouts/DashboardLayout'
import Dashboard from '../pages/Dashboard'
import Scans from '../pages/Scans'
import InvestigationDetails from '../pages/InvestigationDetails'
import Campaigns from '../pages/Campaigns'
import Reports from '../pages/Reports'
import Settings from '../pages/Settings'

// Authentication Components & Pages
import Login from '../auth/pages/Login'
import ForgotPassword from '../auth/pages/ForgotPassword'
import Unauthorized from '../auth/pages/Unauthorized'
import ProtectedRoute from '../auth/components/ProtectedRoute'

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public Authentication Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/unauthorized" element={<Unauthorized />} />

      {/* Protected Enterprise Security Dashboard routes */}
      <Route element={
        <ProtectedRoute>
          <DashboardLayout />
        </ProtectedRoute>
      }>
        {/* Redirect empty paths to the primary Dashboard panel */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/scans" element={<Scans />} />
        <Route path="/scans/:id" element={<InvestigationDetails />} />
        <Route path="/campaigns" element={<Campaigns />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      {/* Wildcard redirect back to secure dashboard or login */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}


