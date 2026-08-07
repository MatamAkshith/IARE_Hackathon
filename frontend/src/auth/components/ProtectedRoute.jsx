import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Route protection wrapper. Ensures that only authorized operators with 
 * necessary permissions can access child routes.
 * 
 * @param {React.ReactNode} children - Component to render if authenticated and permitted
 * @param {string} requiredRole - Optional role requirement (e.g., admin)
 * @param {string} requiredPermission - Optional specific permission requirement (e.g., run:scans)
 */
export default function ProtectedRoute({ 
  children, 
  requiredRole, 
  requiredPermission 
}) {
  const { user, isAuthenticated, loading, hasPermission } = useAuth();
  const location = useLocation();

  // If session is still being decoded, show a themed terminal scanning state
  if (loading) {
    return (
      <div className="min-h-screen bg-[#030712] flex flex-col items-center justify-center space-y-4">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full border-2 border-cyan-500/10" />
          <div className="absolute inset-0 rounded-full border-2 border-t-cyan-500 border-r-cyan-500/30 animate-spin" />
          <div className="absolute inset-2 rounded-full border border-dashed border-cyan-500/20" />
        </div>
        <div className="flex flex-col items-center space-y-1">
          <span className="text-xs font-semibold tracking-widest text-cyan-400 uppercase font-mono animate-pulse">
            Authenticating Session
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            Verifying cryptographic signatures...
          </span>
        </div>
      </div>
    );
  }

  // Not authenticated? Redirect to /login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role requirement
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Check specific permission requirement
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}
