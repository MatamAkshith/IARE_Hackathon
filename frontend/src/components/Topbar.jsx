import React from 'react'
import { useAuth } from '../auth/hooks/useAuth'
import { useNavigate } from 'react-router-dom'

/**
 * Topbar navbar component for the dashboard.
 * 
 * @param {Object} props
 * @param {Function} props.onMenuToggle Callback to open/close the mobile hamburger menu drawer
 */
export default function Topbar({ onMenuToggle }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    if (window.confirm('Terminate secure SOC session?')) {
      await logout()
      navigate('/login')
    }
  }

  const userInitial = user?.user_id ? user.user_id.substring(0, 2).toUpperCase() : 'OP'

  return (
    <header className="h-16 border-b border-[#1a2336] bg-[#090d16] flex items-center justify-between px-6 sticky top-0 z-20">
      <div className="flex items-center gap-4">
        {/* Mobile menu toggle toggle button */}
        <button
          onClick={onMenuToggle}
          aria-label="Toggle Navigation Drawer"
          className="md:hidden p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-[#101726]/60 border border-[#1a2336]"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
 
        {/* Branding header area */}
        <div className="flex items-center gap-2 md:hidden">
          <div className="w-6 h-6 rounded bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center text-[#0b0f19] font-black text-xs">
            TL
          </div>
          <span className="font-extrabold text-slate-100 tracking-wider text-xs uppercase">
            ThreatLens
          </span>
        </div>

        {/* Console Node Status Badge */}
        <div className="hidden md:flex items-center gap-2 text-xs font-mono bg-[#111927] border border-[#1e293b] px-3 py-1.5 rounded-lg">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-slate-400">NODE STATUS:</span>
          <span className="text-slate-200">US-EAST-01</span>
        </div>
      </div>

      {/* User profile and logout area */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="text-right hidden sm:block">
            <span className="block text-[11px] font-bold text-slate-200 uppercase tracking-wide">
              {user?.user_id || 'SOC Analyst'}
            </span>
            <span className="block text-[9px] text-cyan-500 font-mono">
              ROLE: {(user?.role || 'OPERATOR').replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <div className="w-8 h-8 rounded-full bg-cyan-950/40 border border-cyan-800/60 flex items-center justify-center text-xs font-bold text-cyan-400 shadow">
            {userInitial}
          </div>
        </div>

        {/* Secure Logout Button */}
        <button
          onClick={handleLogout}
          title="Sign Out of Session"
          className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-[#1c121b]/40 border border-transparent hover:border-rose-950/60 transition-all duration-200"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </header>
  )
}
