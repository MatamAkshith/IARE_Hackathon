/**
 * AuthContext — Stage E.1
 *
 * Manages enterprise authentication state. Reads real JWTs issued by the
 * backend (/api/v1/auth/login) and calls /api/v1/auth/logout on sign-out.
 *
 * Token payload shape (backend-issued):
 *   { sub: "user_id", role: "analyst", iat: ..., exp: ... }
 */

import React, { createContext, useState, useEffect, useContext } from 'react';
import { getToken, setToken, removeToken, isTokenExpired, decodeToken } from '../utils/jwt';
import { authService } from '../services/authService';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setTokenState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ── Initialize from stored token ───────────────────────────────────────
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const savedToken = getToken();
        if (savedToken) {
          if (isTokenExpired(savedToken)) {
            removeToken();
          } else {
            const decoded = decodeToken(savedToken);
            setTokenState(savedToken);
            setUser({
              user_id: decoded.sub,
              role: decoded.role,
            });
          }
        }
      } catch (err) {
        console.error('[AuthContext] Error initializing authentication:', err);
        removeToken();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();

    // Stage E.5: Inactivity / expiration checker loop (runs every 10s)
    const checkInterval = setInterval(() => {
      const savedToken = getToken();
      if (savedToken && isTokenExpired(savedToken)) {
        console.warn('[AuthContext] Session expired via background timer.');
        removeToken();
        setTokenState(null);
        setUser(null);
        setError(null);
        window.location.href = '/login?session=expired';
      }
    }, 10000);

    return () => clearInterval(checkInterval);
  }, []);

  // Stage G.1: Auto logout on tab close
  useEffect(() => {
    const handleTabClose = () => {
      if (token && user) {
        const baseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
        const url = `${baseUrl}/auth/auto-logout`;
        const payload = JSON.stringify({
          token: token,
          user_id: user.user_id
        });
        const blob = new Blob([payload], { type: 'application/json' });
        navigator.sendBeacon(url, blob);
        
        sessionStorage.removeItem('threatlens_auth_token');
        localStorage.removeItem('threatlens_auth_token');
      }
    };

    window.addEventListener('beforeunload', handleTabClose);
    return () => {
      window.removeEventListener('beforeunload', handleTabClose);
    };
  }, [token, user]);


  // ── Login ──────────────────────────────────────────────────────────────
  /**
   * @param {string} userId
   * @param {string} passkey
   */
  const login = async (userId, passkey) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.login(userId, passkey);

      setTokenState(response.token);
      setToken(response.token);
      setUser(response.user);

      return response.user;
    } catch (err) {
      const message = err?.message || 'Authentication failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  // ── Logout ─────────────────────────────────────────────────────────────
  const logout = async () => {
    const currentToken = token;
    // Clear local state immediately so UI reflects logout
    removeToken();
    setTokenState(null);
    setUser(null);
    setError(null);
    // Best-effort server-side audit log
    if (currentToken) {
      await authService.logout(currentToken).catch(() => {});
    }
  };

  // ── Helpers ────────────────────────────────────────────────────────────
  const hasRole = (role) => user && user.role === role;

  const value = {
    user,
    token,
    loading,
    error,
    login,
    logout,
    hasRole,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
