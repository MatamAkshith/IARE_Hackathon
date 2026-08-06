/**
 * ThreatLens Threat Intelligence & Reports Dataset
 * Centralized dataset representing external feeds reputation metrics.
 */

export const threatIntelligenceData = {
  // 1. External Threat Intelligence Feeds
  threatFeeds: {
    virusTotal: {
      name: 'VirusTotal',
      status: 'Active Connection',
      detectionRatio: '68/72 engines flagged',
      reputation: -15,
      lastAnalysis: '10m ago',
      communityScore: -12,
      riskLevel: 'Critical'
    },
    phishTank: {
      name: 'PhishTank',
      status: 'Active Ingest',
      verifiedStatus: 'Verified Phishing Site',
      phishingReports: 14,
      targetBrand: 'Microsoft Inc.',
      submissionDate: '2026-08-05',
      confidence: '98%'
    },
    urlHaus: {
      name: 'URLHaus',
      status: 'Active Sync',
      malwareFamily: 'AgentTesla Credential Stealer',
      threatCategory: 'credential_harvester',
      urlStatus: 'Active / Malicious',
      hostStatus: 'Online',
      tags: ['phish', 'microsoft', 'credential-stealer', 'exe']
    },
    abuseIPDB: {
      name: 'AbuseIPDB',
      status: 'Active Sync',
      abuseConfidence: '100%',
      country: 'Russia (RU)',
      isp: 'VDSina Server Hosting',
      usageType: 'Data Center / Web Hosting',
      reports: 842,
      lastReported: '2m ago'
    }
  },

  // 2. Indicators of Compromise (IOCs) Table
  iocs: [
    { type: 'Domain', value: 'secure-microsoft-login-verification.com', source: 'VirusTotal', severity: 'critical', confidence: '98%', status: 'Active' },
    { type: 'URL', value: 'https://secure-microsoft-login-verification.com/login/auth.php', source: 'PhishTank', severity: 'critical', confidence: '99%', status: 'Active' },
    { type: 'IP Address', value: '185.230.125.44', source: 'AbuseIPDB', severity: 'high', confidence: '100%', status: 'Active' },
    { type: 'SHA256', value: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', source: 'URLHaus', severity: 'high', confidence: '98%', status: 'Active' },
    { type: 'MD5', value: '5d41402abc4b2a76b9719d911017c592', source: 'URLHaus', severity: 'medium', confidence: '95%', status: 'Active' },
    { type: 'SSL Fingerprint', value: '0a8c2317188bd9a8d9a8c177bd881a8b98ac12ee', source: 'VirusTotal', severity: 'high', confidence: '97%', status: 'Active' },
    { type: 'Email', value: 'admin@secure-microsoft-login-verification.com', source: 'VirusTotal', severity: 'medium', confidence: '90%', status: 'Monitored' },
    { type: 'Favicon Hash', value: '128372648', source: 'VirusTotal', severity: 'medium', confidence: '95%', status: 'Active' }
  ],

  // 3. Reputation Summary
  reputation: {
    verdict: 'Malicious',
    riskLevel: 'Critical',
    score: 98,
    maxScore: 100,
    confidence: '98%',
    recommendation: 'Block Immediately'
  },

  // 4. Analyst Recommendations
  recommendations: [
    'Block all related campaign lookalike domains on firewall and DNS layer.',
    'Monitor shared IP hosting ranges (185.230.125.xx) for new DNS registrations.',
    'Alert internal SOC team of CozyBear campaign infrastructure details.',
    'Push campaign IOCs and hashes to SIEM engine threat library database.',
    'Notify and enforce password resets for enterprise users who hit endpoints.',
    'Continue monitoring attacker nameservers (ns1.fakehost.com) for updates.'
  ],

  // 5. Incident Report Preview details
  reportPreview: {
    title: 'INCIDENT-2026-089 CozyBear Phishing Impersonation Campaign',
    executiveSummary: 'A coordinated phishing and credential harvesting campaign targeting enterprise Microsoft SSO profiles has been flagged. Attackers host lookalike portals on server block 185.230.125.44 sharing registrars credentials, SSL self-signed certificates, and DNS settings.',
    threatDescription: 'Threat actors stage lookalike domains imitating Microsoft login flows. The kit features obfuscated login parameters, remote script references, and validation templates hotlinking official corporate graphics.',
    riskAssessment: 'Risk level is evaluated as CRITICAL based on 100% AbuseIPDB confidence verdicts, 68 engine flags on VirusTotal, and verified phishing URL listings on PhishTank.',
    impact: 'Successful credentials leakages may lead to administrative logins compromises, initial access vector footholds, and email accounts hijacking.',
    timelineSummary: 'Ingestion registered on 2026-08-01. SSL certificate binded on 2026-08-01. Phishing extraction forms detected active on 2026-08-04. Correlation cluster matched on 2026-08-06.',
    indicatorsSummary: '4 lookalike domains, 1 active hosting IP, 1 unique SHA256 file hash, 1 SSL certificate serial, and 9 matching correlation points.',
    analystNotes: 'Attributions correlate strongly to CozyBear (APT29) staging blueprints. Immediate DNS sinkholing, SSO sessions termination, and corporate logins audits are advised.',
    recommendations: 'Implement IP and domain level blocks in active proxy configurations, enforce multi-factor authentication (MFA) parameters, and deploy SIEM logs monitoring rules.'
  },

  // 6. Mock Export Options
  exportOptions: [
    { id: 'executive', name: 'Executive Report', desc: 'Summary report in PDF layout' },
    { id: 'technical', name: 'Technical Report', desc: 'Deep details report in MD layout' },
    { id: 'csv', name: 'IOC CSV List', desc: 'SIEM-compatible CSV checklist' },
    { id: 'json', name: 'JSON Feed Output', desc: 'Structured JSON data objects' }
  ]
}

export default threatIntelligenceData
