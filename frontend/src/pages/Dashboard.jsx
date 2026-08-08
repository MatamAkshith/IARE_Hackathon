import { useNavigate } from 'react-router-dom'
import useDashboard from '../hooks/useDashboard'
import SkeletonLoader from '../components/SkeletonLoader'
import ErrorFallback from '../components/ErrorFallback'
import KPICard from '../components/dashboard/KPICard'
import RecentScansTable from '../components/dashboard/RecentScansTable'
import RiskChart from '../components/dashboard/RiskChart'
import CampaignOverview from '../components/dashboard/CampaignOverview'
import ThreatTimeline from '../components/dashboard/ThreatTimeline'
import ThreatSummary from '../components/dashboard/ThreatSummary'
import StatusPanel from '../components/dashboard/StatusPanel'

import { useAuth } from '../auth/hooks/useAuth'

export default function Dashboard() {
  const navigate = useNavigate()
  const { user, loading: authLoading } = useAuth()
  const { dashboard, loading, error, refetch } = useDashboard()

  if (authLoading || !user) return <SkeletonLoader />

  if (loading) return <SkeletonLoader />
  if (error) return <ErrorFallback message={error} onRetry={refetch} />
  if (!dashboard) return null

  const { kpis, scans, riskDistribution, campaigns, timeline, threatSummary, services } = dashboard

  // Custom inline SVG icons for each KPI card type
  const kpiIcons = {
    'total-scans': (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    'high-risk': (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    'active-campaigns': (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 5.636l-3.536 3.536m0 0 A 4 4 0 1 0 11.293 14.7 a 4.007 4.007 0 0 0 3.535 -3.535 m -3.535 3.535 L 7.757 18.364 m 0 0 A 4 4 0 1 0 3.5 14.12 a 4.007 4.007 0 0 0 4.257 4.243 z" />
      </svg>
    ),
    'avg-risk': (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    'threat-sources': (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172 a 4 4 0 0 0 -5.656 0 l -4 4 a 4 4 0 1 0 5.656 5.656 l 1.102 -1.101 m -0.758 -4.899 a 4 4 0 0 0 5.656 0 l 4 -4 a 4 4 0 0 0 -5.656 -5.656 l -1.1 1.1" />
      </svg>
    ),
    'recent-activity': (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header Area */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Security Operations Center Dashboard</h1>
        <p className="text-xs text-slate-400">
          Real-time ingestion queue monitoring, campaign attributions, and risk assessment indicators.
        </p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpis.map((kpi) => (
          <KPICard
            key={kpi.id}
            title={kpi.title}
            value={kpi.value}
            trend={kpi.trend}
            icon={kpiIcons[kpi.id] || kpiIcons['total-scans']}
            type={kpi.type}
            onClick={kpi.route ? () => navigate(kpi.route) : undefined}
          />
        ))}
      </div>

      {/* Main split grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side: Domain Telemetry Table */}
        <div className="lg:col-span-2 space-y-6">
          <RecentScansTable scans={scans} />
        </div>

        {/* Right Side: Visual widgets stack */}
        <div className="space-y-6">
          <RiskChart data={riskDistribution} />
          
          <CampaignOverview campaigns={campaigns} />
          
          <ThreatSummary summary={threatSummary} />
          
          <ThreatTimeline events={timeline} />
          
          <StatusPanel services={services} />
        </div>
      </div>
    </div>
  )
}
