import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/hooks/useAuth'

export default function Settings() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    if (window.confirm('Terminate secure SOC session?')) {
      await logout()
      navigate('/login')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Console Settings & Feeds Configuration</h1>
        <p className="text-xs text-slate-400">
          Manage API credentials for external intelligence databases (e.g. VirusTotal, PhishTank) and configure default scoring weights.
        </p>
      </div>

      {/* Visual placeholder box */}
      <div className="border border-dashed border-[#1a2336] rounded-xl p-8 bg-[#090d16]/30 text-center text-slate-500 text-xs">
        Threat intelligence API configuration sliders and settings coming soon.
      </div>

      {/* Logout Settings Panel */}
      <div className="border border-[#1a2336] bg-[#090d16] rounded-xl p-6 space-y-4 shadow-md">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Session Management</h3>
        <p className="text-xs text-slate-400">
          Terminate the active operator console session. This will invalidate your security token and write an event to the security audit trail.
        </p>
        <div className="flex items-center gap-4 text-xs font-mono bg-[#0c121e] border border-[#1a2336] p-3.5 rounded-lg w-fit">
          <span className="text-slate-500">OPERATOR ID:</span>
          <span className="text-slate-300 font-bold">{user?.user_id || 'SOC_ANALYST'}</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-500">SECURITY PRIVILEGE:</span>
          <span className="text-cyan-400 font-bold">{(user?.role || 'OPERATOR').replace('_', ' ').toUpperCase()}</span>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="px-4 py-2.5 rounded-lg bg-rose-950/20 border border-rose-800/40 hover:bg-rose-900/30 text-rose-400 hover:text-rose-300 font-bold text-xs uppercase tracking-wider transition-all"
        >
          Terminate Console Session
        </button>
      </div>
    </div>
  )
}
