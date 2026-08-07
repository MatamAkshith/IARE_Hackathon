import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import AuthLayout from '../components/AuthLayout';
import { authService } from '../services/authService';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!email) {
      setError('Please input your registered email address');
      return;
    }

    setIsLoading(true);
    try {
      await authService.forgotPassword(email);
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Key recovery failed. Please verify the address.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="space-y-6">
        {/* Title */}
        <div className="space-y-1">
          <h2 className="text-xl font-bold tracking-tight text-white">Reset Security Key</h2>
          <p className="text-xs text-slate-400">
            {success 
              ? 'Verification guidelines transmitted successfully.' 
              : 'Enter your verified account email to request security reset coordinates.'
            }
          </p>
        </div>

        {success ? (
          <div className="space-y-6">
            <div className="bg-emerald-950/20 border border-emerald-500/30 text-emerald-400 p-4 rounded-lg text-xs space-y-2">
              <div className="flex items-center space-x-2 font-bold uppercase tracking-wider">
                <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Transmission Dispatched</span>
              </div>
              <p className="leading-relaxed">
                If the email address <strong className="font-mono text-white">{email}</strong> matches our records, a secure key recovery link will arrive shortly. Please check your inbox and spam folders.
              </p>
            </div>

            <Link
              to="/login"
              className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-2.5 rounded-lg text-sm transition-colors flex items-center justify-center space-x-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span>Back to Login</span>
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-rose-950/20 border border-rose-500/30 text-rose-400 p-3 rounded-lg text-xs font-medium flex items-start space-x-2">
                <svg className="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            <div className="flex flex-col space-y-1.5 w-full">
              <label htmlFor="email" className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Account Email Address
              </label>
              <div className="relative rounded-lg group">
                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-cyan-500/20 to-blue-500/20 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (error) setError('');
                  }}
                  placeholder="operator@threatlens.io"
                  disabled={isLoading}
                  className="w-full bg-[#0a0f1d] border border-slate-800 focus:border-cyan-500/80 rounded-lg px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200 relative z-10"
                  required
                />
              </div>
            </div>

            <div className="pt-2 space-y-3">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-450 hover:to-blue-550 active:scale-[0.98] text-white font-semibold py-2.5 rounded-lg text-sm transition-all duration-200 flex items-center justify-center space-x-2 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 shadow-[0_4px_20px_rgba(6,182,212,0.25)]"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Requesting Reset...</span>
                  </>
                ) : (
                  <span>Send Recovery Instructions</span>
                )}
              </button>

              <Link
                to="/login"
                className="w-full bg-[#0a0f1d] border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 font-semibold py-2.5 rounded-lg text-sm transition-colors flex items-center justify-center space-x-2"
              >
                <span>Return to Login</span>
              </Link>
            </div>
          </form>
        )}

        {/* Info text */}
        <div className="mt-8 pt-4 border-t border-slate-800/40 text-center text-[10px] text-slate-500 font-mono">
          SECURE ENCRYPTED CHANNEL
        </div>
      </div>
    </AuthLayout>
  );
}
