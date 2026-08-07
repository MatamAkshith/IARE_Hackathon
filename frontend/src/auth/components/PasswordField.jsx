import React, { useState } from 'react';

/**
 * Reusable password field component with toggleable show/hide behavior
 * and modern cyber-inspired input styling.
 */
export default function PasswordField({ 
  value, 
  onChange, 
  id = 'password', 
  name = 'password',
  placeholder = '••••••••',
  label = 'Security Key (Password)',
  error,
  disabled
}) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="flex flex-col space-y-1.5 w-full">
      <div className="flex justify-between items-center">
        <label htmlFor={id} className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
          {label}
        </label>
      </div>

      <div className="relative rounded-lg group">
        {/* Decorative inner glow focus line */}
        <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-cyan-500/20 to-blue-500/20 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        
        <input
          type={showPassword ? 'text' : 'password'}
          id={id}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          className={`w-full bg-[#0a0f1d] border ${error ? 'border-rose-500/60' : 'border-slate-800 group-hover:border-slate-700'} focus:border-cyan-500/80 rounded-lg px-4 py-2.5 pr-10 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200 relative z-10`}
        />

        {/* Show/Hide password toggle button */}
        <button
          type="button"
          onClick={() => setShowPassword(prev => !prev)}
          disabled={disabled}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors z-20 focus:outline-none"
          tabIndex="-1"
        >
          {showPassword ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              {/* Eye Off Icon */}
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              {/* Eye Icon */}
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          )}
        </button>
      </div>
      
      {error && (
        <span className="text-xs text-rose-500 font-medium pl-1">
          {error}
        </span>
      )}
    </div>
  );
}
