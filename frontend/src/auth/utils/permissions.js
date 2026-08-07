import { ROLES } from './roles';

/**
 * System-wide permissions list
 */
export const PERMISSIONS = {
  VIEW_DASHBOARD: 'view:dashboard',
  RUN_SCANS: 'run:scans',
  MANAGE_CAMPAIGNS: 'manage:campaigns',
  EXPORT_REPORTS: 'export:reports',
  MANAGE_SETTINGS: 'manage:settings',
};

/**
 * Role-to-Permissions Mapping
 */
export const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.RUN_SCANS,
    PERMISSIONS.MANAGE_CAMPAIGNS,
    PERMISSIONS.EXPORT_REPORTS,
    PERMISSIONS.MANAGE_SETTINGS,
  ],
  [ROLES.ANALYST]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.RUN_SCANS,
    PERMISSIONS.MANAGE_CAMPAIGNS,
    PERMISSIONS.EXPORT_REPORTS,
  ],
  [ROLES.AUDITOR]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.EXPORT_REPORTS,
  ],
};

/**
 * Check if a given role has a specific permission
 * @param {string} role 
 * @param {string} permission 
 * @returns {boolean}
 */
export const hasPermission = (role, permission) => {
  if (!role) return false;
  const permissions = ROLE_PERMISSIONS[role] || [];
  return permissions.includes(permission);
};
