import React from 'react'

/**
 * Reusable error boundary fallback card.
 * 
 * @param {Object} props
 * @param {string} props.message Main error message text
 * @param {Function} props.onRetry Callback to retry loading dataset
 */
export default function ErrorFallback({ message, onRetry }) {
  return (
    <div className="border border-rose-900 bg-rose-950/10 p-6 rounded-xl flex flex-col items-center justify-center text-center space-y-4 max-w-md mx-auto my-12 shadow-lg shadow-rose-500/5">
      <div className="p-3 rounded-full bg-rose-950/30 text-rose-400 border border-rose-900/40">
        <svg className="w-8 h-8 stroke-[2.5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>

      <div className="space-y-1">
        <h4 className="text-sm font-black text-slate-100 uppercase tracking-wider">
          Telemetry Load Failure
        </h4>
        <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
          {message || 'An unexpected error occurred while parsing telemetry feed.'}
        </p>
      </div>

      <button
        type="button"
        onClick={onRetry}
        className="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-slate-900 font-extrabold rounded-lg text-xs uppercase tracking-wider shadow-lg shadow-rose-500/10 transition-colors"
      >
        Retry Connection
      </button>
    </div>
  )
}
