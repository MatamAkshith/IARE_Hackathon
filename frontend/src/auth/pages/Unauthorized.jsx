import React from 'react';
import { Link } from 'react-router-dom';
import AuthLayout from '../components/AuthLayout';
import { useAuth } from '../hooks/useAuth';

export default function Unauthorized() {
  const { user, logout } = useAuth();

  return (
    <AuthLayout>
      <div className="space-y-6 text-center">
        {/* Warning Icon */}
        <div className="mx-auto w-16 h-16 rounded-full bg-rose-950/30 border border-rose-500/30 flex items-center justify-center text-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.15)] animate-pulse">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>

        {/* Title */}
        <div className="space-y-1">
          <h2 className="text-xl font-bold tracking-tight text-white uppercase text-rose-500">Clearance Denied</h2>
          <p className="text-xs text-slate-400">
            Access to this directory requires higher cryptographic permissions.
          </p>
        </div>

        {/* Details Card */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 text-xs text-left space-y-2 font-mono">
          <div className="flex justify-between">
            <span className="text-slate-500">ACTIVE OPERATOR:</span>
            <span className="text-slate-300 font-semibold">{user?.name || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">CLEARANCE ROLE:</span>
            <span className="text-cyan-400 font-bold uppercase">{user?.role || 'Guest / None'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">PLATFORM ERROR:</span>
            <span className="text-rose-400">HTTP_403_FORBIDDEN</span>
          </div>
        </div>

        {/* Navigation actions */}
        <div className="space-y-3 pt-2">
          <Link
            to="/dashboard"
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-450 hover:to-blue-550 active:scale-[0.98] text-white font-semibold py-2.5 rounded-lg text-sm transition-all duration-200 flex items-center justify-center space-x-2 shadow-[0_4px_15px_rgba(6,182,212,0.2)]"
          >
            <span>Return to Dashboard</span>
          </Link>
          
          <button
            type="button"
            onClick={logout}
            className="w-full bg-[#0a0f1d] border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 font-semibold py-2.5 rounded-lg text-sm transition-colors flex items-center justify-center space-x-2"
          >
            <span>Re-authorize Different Account</span>
          </button>
        </div>

        {/* Footer info */}
        <div className="mt-8 pt-4 border-t border-slate-800/40 text-center text-[10px] text-slate-500 font-mono">
          SECURITY PROTOCOL SEC-403 ACTIVE
        </div>
      </div>
    </AuthLayout>
  );
}
