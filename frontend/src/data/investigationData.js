/**
 * ThreatLens Static URL Investigation Telemetry Dataset
 * Centralized dataset representing lookalike domain evidence.
 */

export const investigationData = {
  url: 'secure-microsoft-login-verification.com',
  
  // Risk Score metrics
  risk: {
    score: 92,
    maxScore: 100,
    level: 'Critical',
    recommendation: 'Block immediately',
    confidence: '98%',
    badgeColor: 'bg-rose-950/20 text-rose-400 border-rose-800/40 shadow-rose-500/10'
  },

  // Narrative bullet indicators
  explanation: [
    'Newly registered domain (registered less than 3 days ago).',
    'Brand impersonation detected (lookalike patterns targeting "Microsoft").',
    'Invalid or Untrusted SSL certificate (Self-Signed certificate).',
    'Suspicious HTML login form structure containing active input password boxes.',
    'Multiple phishing indicators identified matching known credential harvesting campaigns.'
  ],

  // Badges of finding tags
  badges: [
    { label: 'New Domain', type: 'danger' },
    { label: 'Self Signed SSL', type: 'danger' },
    { label: 'Credential Harvesting', type: 'danger' },
    { label: 'Brand Impersonation', type: 'warning' },
    { label: 'High Entropy URL', type: 'warning' },
    { label: 'Recently Registered', type: 'info' }
  ],

  // Category evidence lists
  evidence: {
    domain: [
      { label: 'Domain Name', value: 'secure-microsoft-login-verification.com', mono: true },
      { label: 'TLD Suffix', value: '.com', mono: true },
      { label: 'Registrar Authority', value: 'Unknown / Redacted', highlight: true },
      { label: 'Registration Date', value: '3 days ago (2026-08-03)', highlight: true },
      { label: 'Hosting Country Code', value: 'Unknown / Hidden' }
    ],
    dns: [
      { label: 'A Record (IP Mapping)', value: '185.230.125.44', mono: true },
      { label: 'MX Record (Mail Exchange)', value: 'Present (mail.fakehost.com)', mono: true },
      { label: 'NS Records (Nameservers)', value: 'ns1.fakehost.com, ns2.fakehost.com', mono: true }
    ],
    whois: [
      { label: 'WHOIS Registrar', value: 'NameCheap, Inc.', mono: true },
      { label: 'Creation Timestamp', value: '3 days ago (2026-08-03T14:22:00Z)' },
      { label: 'Registry Expiration', value: '1 year (2027-08-03T14:22:00Z)' },
      { label: 'Registrant Identity', value: 'Privacy Service Provided by Withheld for Privacy ehf', highlight: true }
    ],
    ssl: [
      { label: 'Certificate Issuer', value: 'Self Signed (Fake Microsoft CA)', highlight: true },
      { label: 'SSL Active Handshake', value: 'No (Untrusted Authority)', highlight: true },
      { label: 'Days until Expiration', value: 'Invalid (Expired 2026-08-01)', highlight: true },
      { label: 'Encryption Key Size', value: 'RSA 2048-bit', mono: true }
    ],
    html: [
      { label: 'Webpage HTML Title', value: 'Microsoft Secure Login' },
      { label: 'Total Input Forms', value: '2' },
      { label: 'External Scripts Referenced', value: '8 (Asset scraping indicator)', highlight: true },
      { label: 'Hidden Input Parameters', value: '5 (Token tracking typical in phish kits)', mono: true },
      { label: 'Suspicious Keywords Flagged', value: 'password, verify, account', highlight: true }
    ],
    metadata: [
      { label: 'HTTP Response Code', value: '200 OK', mono: true },
      { label: 'Content Type Specification', value: 'text/html; charset=utf-8', mono: true },
      { label: 'WebServer Signature', value: 'nginx/1.24.0', mono: true },
      { label: 'Redirect Chain Hops', value: '2 (Redirect from http to secure https)', mono: true }
    ]
  }
}

export default investigationData
