import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import PasswordField from './PasswordField';
import RememberMe from './RememberMe';

export default function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState({});
  
  // Service loading & error states
  const [isLoading, setIsLoading] = useState(false);
  const [authError, setAuthError] = useState('');

  // Validate form entries
  const validateForm = () => {
    const newErrors = {};
    if (!email) {
      newErrors.email = 'Identifier email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Invalid email structure (e.g. name@domain.com)';
    }

    if (!password) {
      newErrors.password = 'Credential key is required';
    } else if (password.length < 6) {
      newErrors.password = 'Key must contain at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Quick select credentials for testing mock login flow
  const autofillCredentials = (roleEmail, rolePassword) => {
    setEmail(roleEmail);
    setPassword(rolePassword);
    setErrors({});
    setAuthError('');
  };

  // Form submit handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');

    if (!validateForm()) return;

    setIsLoading(true);
    try {
      await login(email, password, rememberMe);
      // Redirect on successful authentication to dashboard
      // Note: we can redirect to /dashboard since we want to follow auth architecture flow.
      // But we shouldn't modify the existing dashboard. The user will be redirected there.
      navigate('/dashboard');
    } catch (err) {
      setAuthError(err.message || 'Login attempt failed. Please check network logs.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div className="space-y-1">
        <h2 className="text-xl font-bold tracking-tight text-white">Console Authorization</h2>
        <p className="text-xs text-slate-400">Enter security credentials to decrypt and access session.</p>
      </div>

      {/* Auth Error Banner */}
      {authError && (
        <div className="bg-rose-950/20 border border-rose-500/30 text-rose-400 p-3 rounded-lg text-xs font-medium flex items-start space-x-2 animate-shake">
          <svg className="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{authError}</span>
        </div>
      )}

      {/* Input Fields */}
      <div className="space-y-4">
        {/* Email Field */}
        <div className="flex flex-col space-y-1.5 w-full">
          <label htmlFor="email" className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Identity Email
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
                if (errors.email) setErrors(prev => ({ ...prev, email: null }));
              }}
              placeholder="operator@threatlens.io"
              disabled={isLoading}
              className={`w-full bg-[#0a0f1d] border ${errors.email ? 'border-rose-500/60' : 'border-slate-800 group-hover:border-slate-700'} focus:border-cyan-500/80 rounded-lg px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200 relative z-10`}
            />
          </div>
          {errors.email && (
            <span className="text-xs text-rose-500 font-medium pl-1">{errors.email}</span>
          )}
        </div>

        {/* Password Field */}
        <PasswordField
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (errors.password) setErrors(prev => ({ ...prev, password: null }));
          }}
          error={errors.password}
          disabled={isLoading}
        />
      </div>

      {/* Utilities: Remember Me & Forgot Password */}
      <div className="flex items-center justify-between">
        <RememberMe
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
          disabled={isLoading}
        />
        <Link
          to="/forgot-password"
          className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          Recover Key
        </Link>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-450 hover:to-blue-550 active:scale-[0.98] text-white font-semibold py-2.5 rounded-lg text-sm transition-all duration-200 flex items-center justify-center space-x-2 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 shadow-[0_4px_20px_rgba(6,182,212,0.25)] hover:shadow-[0_4px_25px_rgba(6,182,212,0.4)] disabled:opacity-50 disabled:pointer-events-none"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>Decrypting Identity...</span>
          </>
        ) : (
          <span>Authorize Access</span>
        )}
      </button>

      {/* Mock Autofill Accounts Widget for testing */}
      <div className="mt-6 pt-5 border-t border-slate-800/60 space-y-2.5">
        <div className="flex justify-between items-center">
          <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Simulator Safe Credentials</span>
          <span className="text-[9px] bg-cyan-950/40 text-cyan-400 border border-cyan-800/30 px-1.5 py-0.5 rounded uppercase font-mono">Mock Auth Enabled</span>
        </div>
        <div className="grid grid-cols-3 gap-2">
          <button
            type="button"
            onClick={() => autofillCredentials('admin@threatlens.io', 'adminPassword123!')}
            className="bg-[#0c1223] border border-slate-800 hover:border-cyan-500/50 rounded p-1.5 text-left transition-colors group"
          >
            <span className="block text-[10px] font-bold text-slate-300 group-hover:text-cyan-400">Admin</span>
            <span className="block text-[8px] font-mono text-slate-500 mt-0.5">admin@threatlens.io</span>
          </button>
          <button
            type="button"
            onClick={() => autofillCredentials('analyst@threatlens.io', 'analystPassword123!')}
            className="bg-[#0c1223] border border-slate-800 hover:border-cyan-500/50 rounded p-1.5 text-left transition-colors group"
          >
            <span className="block text-[10px] font-bold text-slate-300 group-hover:text-cyan-400">Analyst</span>
            <span className="block text-[8px] font-mono text-slate-500 mt-0.5">analyst@...</span>
          </button>
          <button
            type="button"
            onClick={() => autofillCredentials('auditor@threatlens.io', 'auditorPassword123!')}
            className="bg-[#0c1223] border border-slate-800 hover:border-cyan-500/50 rounded p-1.5 text-left transition-colors group"
          >
            <span className="block text-[10px] font-bold text-slate-300 group-hover:text-cyan-400">Auditor</span>
            <span className="block text-[8px] font-mono text-slate-500 mt-0.5">auditor@...</span>
          </button>
        </div>
      </div>
    </form>
  );
}
