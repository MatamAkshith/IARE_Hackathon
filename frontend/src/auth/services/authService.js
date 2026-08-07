/**
 * Authentication Service — Stage E.1
 *
 * Replaces the mock user lookup with real calls to the ThreatLens backend:
 *   POST /api/v1/auth/login   → returns { access_token, token_type, user_id, role }
 *   POST /api/v1/auth/logout  → writes server-side audit log entry
 *
 * All sensitive credential verification is now performed on the backend.
 * No mock users, no client-side password checks.
 */

import apiClient from '../../api/client';

export const authService = {
  /**
   * Authenticate an enterprise employee with user_id + passkey.
   * @param {string} userId  — ThreatLens employee ID (e.g. "analyst01")
   * @param {string} passkey — Passkey string
   * @returns {Promise<{ token: string, user: { user_id, role } }>}
   */
  login: async (userId, passkey) => {
    const data = await apiClient.post('/auth/login', {
      user_id: userId,
      passkey: passkey,
    });

    return {
      token: data.access_token,
      user: {
        user_id: data.user_id,
        role: data.role,
      },
    };
  },

  /**
   * Terminate the authenticated session server-side (audit log).
   * The caller should remove the token from localStorage afterwards.
   * @param {string} token — current Bearer token
   * @returns {Promise<void>}
   */
  logout: async (token) => {
    try {
      await apiClient.post(
        '/auth/logout',
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch {
      // Swallow logout errors — we clear the local token regardless
    }
  },
};
