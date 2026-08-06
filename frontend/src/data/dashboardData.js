/**
 * ThreatLens Static SOC Telemetry Dataset
 * Centralized dashboard data model simulating a live threat inspection pipeline.
 */

export const dashboardData = {
  // KPI Metrics
  kpis: [
    {
      id: 'total-scans',
      title: 'Total Scans',
      value: '1,248',
      trend: { value: '+14%', positive: true },
      type: 'neutral'
    },
    {
      id: 'high-risk',
      title: 'High Risk Domains',
      value: '342',
      trend: { value: '+8%', positive: false },
      type: 'warning'
    },
    {
      id: 'active-campaigns',
      title: 'Active Campaigns',
      value: '18',
      trend: { value: '+3', positive: false },
      type: 'danger'
    },
    {
      id: 'avg-risk',
      title: 'Avg Risk Score',
      value: '64.2',
      trend: { value: '-2.4%', positive: true }, // lowering avg risk is positive
      type: 'info'
    },
    {
      id: 'threat-sources',
      title: 'Threat Feeds',
      value: '5/5',
      trend: { value: '100% active', positive: true },
      type: 'success'
    },
    {
      id: 'recent-activity',
      title: 'Recent Activity (24h)',
      value: '84',
      trend: { value: '+12%', positive: false },
      type: 'neutral'
    }
  ],

  // Recent Domain Scans
  scans: [
    {
      id: 1,
      domain: 'paypal-verify-secure.com',
      riskScore: 92,
      status: 'completed',
      scanTime: '2026-08-06 22:15',
      campaign: 'Paypal Credential Harvester Wave'
    },
    {
      id: 2,
      domain: 'microsoft-login-update.net',
      riskScore: 88,
      status: 'completed',
      scanTime: '2026-08-06 21:40',
      campaign: 'CozyBear Microsoft Impersonation'
    },
    {
      id: 3,
      domain: 'chase-security-alert.org',
      riskScore: 45,
      status: 'completed',
      scanTime: '2026-08-06 20:30',
      campaign: 'Chase Bank Lookalike Campaign'
    },
    {
      id: 4,
      domain: 'secure-bank-login.xyz',
      riskScore: 95,
      status: 'completed',
      scanTime: '2026-08-06 19:15',
      campaign: 'Uncorrelated / Individual Threat'
    },
    {
      id: 5,
      domain: 'google-drive-share.info',
      riskScore: 78,
      status: 'completed',
      scanTime: '2026-08-06 18:50',
      campaign: 'Uncorrelated / Individual Threat'
    },
    {
      id: 6,
      domain: 'netflix-account-restore.com',
      riskScore: 12,
      status: 'completed',
      scanTime: '2026-08-06 17:30',
      campaign: 'Netflix Scrape Wave'
    },
    {
      id: 7,
      domain: 'dhl-tracking-portal.net',
      riskScore: 68,
      status: 'processing',
      scanTime: '2026-08-06 17:15',
      campaign: 'DHL Delivery Phish Wave'
    },
    {
      id: 8,
      domain: 'apple-id-verify.support',
      riskScore: null,
      status: 'failed',
      scanTime: '2026-08-06 16:45',
      campaign: 'Uncorrelated / Individual Threat'
    }
  ],

  // Risk Scores distribution counts
  riskDistribution: [
    { label: 'Safe (0-39)', count: 486, percentage: 39, color: 'bg-emerald-500' },
    { label: 'Medium (40-69)', count: 420, percentage: 34, color: 'bg-amber-500' },
    { label: 'High (70-89)', count: 242, percentage: 19, color: 'bg-orange-500' },
    { label: 'Critical (90-100)', count: 100, percentage: 8, color: 'bg-rose-500' }
  ],

  // Campaigns status summary
  campaigns: [
    { label: 'Active Monitoring', count: 12, color: 'text-brand-400 bg-brand-950/20 border-brand-900/30' },
    { label: 'Investigating', count: 4, color: 'text-amber-400 bg-amber-950/20 border-amber-900/30' },
    { label: 'Completed Takedown', count: 18, color: 'text-emerald-400 bg-emerald-950/20 border-emerald-900/30' },
    { label: 'Archived / Inactive', count: 32, color: 'text-slate-400 bg-slate-900/20 border-slate-800/30' }
  ],

  // Activity events timeline
  timeline: [
    { time: '22:15', type: 'critical', message: 'Critical threat score [92] computed for paypal-verify-secure.com' },
    { time: '21:40', type: 'high', message: 'CozyBear Microsoft Impersonation Campaign footprint detected on microsoft-login-update.net' },
    { time: '20:30', type: 'medium', message: 'Active Scan completed Chase bank lookalike domain chase-security-alert.org' },
    { time: '19:15', type: 'critical', message: 'Credential harvesting form detected on secure-bank-login.xyz' },
    { time: '17:15', type: 'info', message: 'New extraction container initialized for dhl-tracking-portal.net' },
    { time: '16:45', type: 'error', message: 'SSL verification failed for apple-id-verify.support (pipeline timeout)' }
  ],

  // Highlight details summary
  threatSummary: {
    mostTargetedBrand: 'PayPal Inc.',
    mostCommonAttack: 'Credential Harvesting',
    mostCommonTLD: '.com (54%)',
    highestRiskDomain: 'secure-bank-login.xyz (95)',
    latestScan: 'paypal-verify-secure.com (22:15)'
  },

  // Mock status monitors
  services: [
    { name: 'Core API Server', status: 'Offline', color: 'bg-rose-500' },
    { name: 'PostgreSQL DB Engine', status: 'Offline', color: 'bg-rose-500' },
    { name: 'Intel Feeds Connector', status: 'Offline', color: 'bg-rose-500' },
    { name: 'Explainable AI Engine', status: 'Offline', color: 'bg-rose-500' }
  ]
}

export default dashboardData
