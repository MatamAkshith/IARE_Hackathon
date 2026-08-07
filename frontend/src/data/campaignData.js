/**
 * ThreatLens Campaign Intelligence Dataset
 * Centralized dataset representing lookalike domain campaign correlation.
 */

export const campaignData = {
  // 1. Campaign Overview Summary
  summary: {
    campaignName: 'CozyBear Impersonation Wave',
    campaignId: 'CAMP-2026-004',
    status: 'Active',
    riskLevel: 'Critical',
    confidence: '97%',
    firstSeen: '2026-08-01 08:15',
    lastSeen: '2026-08-06 22:15',
    totalDomains: 4,
    activeDomains: 4,
    infrastructureCount: 7,
    iocs: [
      '185.230.125.44',
      'secure-microsoft-login-verification.com',
      'office365-security-check.net',
      'microsoft-login-auth.live',
      'login-update-portal.co',
      'ns1.fakehost.com',
      'SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    ]
  },

  // 2. Connected Domains List
  connectedDomains: [
    {
      id: 1,
      domain: 'secure-microsoft-login-verification.com',
      riskScore: 92,
      status: 'active',
      firstSeen: '2026-08-03 14:22',
      lastSeen: '2026-08-06 22:15',
      country: 'Unknown (Privacy Protected)',
      hostingProvider: 'GlobalHost Corp'
    },
    {
      id: 2,
      domain: 'office365-security-check.net',
      riskScore: 88,
      status: 'active',
      firstSeen: '2026-08-01 08:15',
      lastSeen: '2026-08-06 21:40',
      country: 'Unknown (Privacy Protected)',
      hostingProvider: 'GlobalHost Corp'
    },
    {
      id: 3,
      domain: 'microsoft-login-auth.live',
      riskScore: 84,
      status: 'active',
      firstSeen: '2026-08-04 10:05',
      lastSeen: '2026-08-06 18:30',
      country: 'United States',
      hostingProvider: 'GlobalHost Corp'
    },
    {
      id: 4,
      domain: 'login-update-portal.co',
      riskScore: 78,
      status: 'active',
      firstSeen: '2026-08-05 11:30',
      lastSeen: '2026-08-06 15:50',
      country: 'Canada',
      hostingProvider: 'GlobalHost Corp'
    }
  ],

  // 3. Shared Infrastructure
  infrastructure: {
    ipAddress: '185.230.125.44',
    asn: 'AS41235 (FakeNetwork Inc.)',
    hostingProvider: 'GlobalHost Corp',
    registrar: 'NameCheap, Inc.',
    nameservers: 'ns1.fakehost.com, ns2.fakehost.com',
    sslFingerprint: 'SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    whoisSimilarity: '94% Match (Registrant, Email, Phone Redacted)'
  },

  // 4. Shared Correlation Evidence
  sharedEvidence: [
    { type: 'WHOIS Match', description: 'All domains registered via NameCheap with privacy shield.', severity: 'medium', confidence: '95%' },
    { type: 'SSL Fingerprint Match', description: 'CozyBear fake self-signed cert deployed across endpoints.', severity: 'high', confidence: '98%' },
    { type: 'HTML Similarity', description: '99% identical Microsoft login templates structure.', severity: 'high', confidence: '99%' },
    { type: 'Logo Match', description: 'Hotlinked official Microsoft icons and CSS templates.', severity: 'high', confidence: '97%' },
    { type: 'Favicon Hash Match', description: 'Identical favicon hash found on all index tags.', severity: 'medium', confidence: '95%' },
    { type: 'JavaScript Fingerprint', description: 'Shared credential harvester obfuscation script.', severity: 'high', confidence: '98%' },
    { type: 'Hosting Match', description: 'All resolved domains host on IP range 185.230.125.xx.', severity: 'medium', confidence: '90%' },
    { type: 'Registrar Match', description: 'All domains registered near-simultaneously via NameCheap.', severity: 'low', confidence: '85%' },
    { type: 'DNS Match', description: 'Domains configured with nameservers ns1.fakehost.com.', severity: 'high', confidence: '95%' }
  ],

  // 5. Confidence Indicators
  confidence: {
    score: 97,
    severity: 'Critical',
    sharedIndicators: 9,
    correlatedDomains: 4,
    recommendation: 'Block resolved IP range immediately and initiate corporate credential resets.'
  },

  // 6. Campaign timeline logs
  timeline: [
    { time: '2026-08-01 08:15', title: 'First Domain Registered', desc: 'office365-security-check.net registered via NameCheap.' },
    { time: '2026-08-01 09:30', title: 'SSL Certificate Issued', desc: 'Self-signed certificate created and binded to port 443.' },
    { time: '2026-08-03 14:22', title: 'Additional Domain Registered', desc: 'secure-microsoft-login-verification.com registered via NameCheap.' },
    { time: '2026-08-03 15:10', title: 'Infrastructure Reused', desc: 'Domain secure-microsoft-login-verification.com resolved to 185.230.125.44.' },
    { time: '2026-08-04 10:05', title: 'Credential Harvesting Detected', desc: 'Active login structures and password forms flagged on microsoft-login-auth.live.' },
    { time: '2026-08-05 11:30', title: 'Latest Activity', desc: 'New domain login-update-portal.co registered and linked to nameservers ns1.fakehost.com.' }
  ]
}

export default campaignData
