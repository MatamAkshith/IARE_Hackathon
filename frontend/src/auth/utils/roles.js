/**
 * Roles configuration for ThreatLens SOC Platform
 */
export const ROLES = {
  ADMIN: 'admin',         // Full access: Security Administrator
  ANALYST: 'analyst',     // Read/Write access: SOC Analyst
  AUDITOR: 'auditor'      // Read-only access: Auditor / Viewer
};

export const ROLE_LABELS = {
  [ROLES.ADMIN]: 'Security Administrator',
  [ROLES.ANALYST]: 'SOC Analyst',
  [ROLES.AUDITOR]: 'Auditor'
};
