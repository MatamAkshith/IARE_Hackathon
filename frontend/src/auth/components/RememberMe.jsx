import React from 'react';

/**
 * Reusable cyber-styled checkbox component for remember me logic.
 */
export default function RememberMe({ checked, onChange, disabled }) {
  return (
    <label className="flex items-center space-x-2.5 cursor-pointer group select-none">
      <div className="relative flex items-center">
        <input
          type="checkbox"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          className="sr-only"
        />
        {/* Custom styled checkbox indicator */}
        <div className={`w-4 h-4 rounded border transition-all duration-200 flex items-center justify-center 
          ${checked 
            ? 'bg-cyan-500 border-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.4)]' 
            : 'bg-[#0a0f1d] border-slate-800 group-hover:border-slate-600'
          }`}
        >
          {checked && (
            <svg className="w-2.5 h-2.5 text-[#030712] font-extrabold" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="4.5" d="M5 13l4 4L19 7" />
            </svg>
          )}
        </div>
      </div>
      <span className="text-xs text-slate-400 group-hover:text-slate-300 font-medium transition-colors">
        Remember active session
      </span>
    </label>
  );
}
