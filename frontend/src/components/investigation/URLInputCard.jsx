import React from 'react'

/**
 * URL Submission panel card for inputting suspicious web targets.
 * 
 * @param {Object} props
 * @param {string} props.value Current input URL value
 * @param {Function} props.onChange Input change callback
 * @param {Function} props.onScan Submit scan callback
 * @param {Function} props.onClear Reset input fields callback
 * @param {boolean} props.disabled Disables controls during scan processing
 */
export default function URLInputCard({ value, onChange, onScan, onClear, disabled }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    if (value.trim()) {
      onScan()
    }
  }

  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl shadow-md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="suspicious-url" className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Suspicious Target URL
          </label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
            </span>
            <input
              type="text"
              id="suspicious-url"
              placeholder="e.g. https://secure-microsoft-login-verification.com"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              disabled={disabled}
              className="w-full pl-10 pr-4 py-2.5 bg-[#0e1422] border border-[#1a2336] rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all font-mono disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={disabled || !value.trim()}
            className="flex-1 py-2.5 bg-brand-600 hover:bg-brand-500 text-slate-900 font-extrabold rounded-lg text-xs tracking-wider shadow-lg shadow-brand-500/10 transition-all uppercase flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {disabled ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-slate-900" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Extracting Telemetry...
              </>
            ) : (
              'Analyze Target'
            )}
          </button>
          
          <button
            type="button"
            onClick={onClear}
            disabled={disabled || !value}
            className="px-5 py-2.5 bg-[#0e1422] border border-slate-700/50 hover:bg-[#151d2f] text-slate-400 hover:text-slate-200 rounded-lg text-xs font-semibold uppercase transition-colors disabled:opacity-50"
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  )
}
