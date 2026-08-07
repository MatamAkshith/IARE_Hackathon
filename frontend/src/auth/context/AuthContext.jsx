import React, { createContext, useState, useEffect, useContext } from 'react';
import { getToken, setToken, removeToken, decodeMockToken, isTokenExpired } from '../utils/jwt';
import { authService } from '../services/authService';
import { hasPermission as checkPermission } from '../utils/permissions';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setTokenState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize and check token on load
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const savedToken = getToken();
        if (savedToken) {
          if (isTokenExpired(savedToken)) {
            // Token expired, log user out
            removeToken();
          } else {
            // Token is valid, decode and set user session
            const decoded = decodeMockToken(savedToken);
            setTokenState(savedToken);
            setUser({
              email: decoded.email,
              name: decoded.name,
              role: decoded.role,
              title: decoded.title
            });
          }
        }
      } catch (err) {
        console.error('Error initializing authentication:', err);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email, password, rememberMe = false) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.login(email, password);
      
      setTokenState(response.token);
      setUser(response.user);
      
      // If remember me is checked, save to localStorage (handled by setToken)
      // Note: in a real implementation we could configure token TTLs or session storage,
      // here we simplify to always setting token in localStorage for session persistency.
      setToken(response.token);
      
      return response.user;
    } catch (err) {
      setError(err.message || 'Authentication failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    removeToken();
    setTokenState(null);
    setUser(null);
    setError(null);
  };

  const hasRole = (role) => {
    return user && user.role === role;
  };

  const hasPermission = (permission) => {
    return user && checkPermission(user.role, permission);
  };

  const value = {
    user,
    token,
    loading,
    error,
    login,
    logout,
    hasRole,
    hasPermission,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
