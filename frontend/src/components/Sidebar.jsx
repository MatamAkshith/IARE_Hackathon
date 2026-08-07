import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/hooks/useAuth'

/**
 * Sidebar navigation component for threat logs and intelligence metrics.
 * 
 * @param {Object} props
 * @param {Function} [props.onItemClick] Optional callback executed when clicking navigation links (used to dismiss mobile overlays)
 */
export default function Sidebar({ onItemClick }) {
  const { user } = useAuth()

  // Navigation item configurations
  const menuItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z" />
        </svg>
      )
    },
    {
      label: 'Scans',
      path: '/scans',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7 a 2 2 0 0 0 -2 2 v12 a 2 2 0 0 0 2 2 h10 a 2 2 0 0 0 2 -2 V7 a 2 2 0 0 0 -2 -2 h-2 M9 5 a 2 2 0 0 0 2 2 h2 a 2 2 0 0 0 2 -2 M9 5 a 2 2 0 0 1 2 -2 h2 a 2 2 0 0 1 2 2 m -3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
      )
    },
    {
      label: 'Campaigns',
      path: '/campaigns',
      allowedRoles: ['admin', 'soc_lead', 'threat_intel', 'security_manager'],
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      )
    },
    {
      label: 'Reports',
      path: '/reports',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7 a 2 2 0 0 1 -2 -2 V5 a 2 2 0 0 1 2 -2 h5.586 a 1 1 0 0 1 0.707 0.293 l5.414 5.414 a 1 1 0 0 1 0.293 0.707 V19 a 2 2 0 0 1 -2 2 z" />
        </svg>
      )
    },
    {
      label: 'Settings',
      path: '/settings',
      allowedRoles: ['admin', 'soc_lead', 'security_manager'],
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      )
    }
  ]

  // Filter items based on active user role
  const visibleItems = menuItems.filter(
    (item) => !item.allowedRoles || (user && item.allowedRoles.includes(user.role))
  )

  const userInitial = user?.user_id ? user.user_id.substring(0, 2).toUpperCase() : 'OP'

  return (
    <div className="flex flex-col h-full bg-[#090d16] border-r border-[#1a2336]">
      {/* Brand logo container */}
      <div className="h-16 flex items-center px-6 border-b border-[#1a2336] gap-3 bg-[#0c121e]">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center text-[#0b0f19] font-extrabold text-base shadow-lg shadow-brand-500/20">
          TL
        </div>
        <div>
          <span className="font-extrabold text-slate-100 tracking-wider text-sm block">ThreatLens</span>
          <span className="text-[10px] text-brand-400 uppercase tracking-widest font-semibold block mt-[-2px]">
            Security Ops
          </span>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            onClick={onItemClick}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
                isActive
                  ? 'bg-brand-900/35 text-brand-300 border-l-2 border-brand-500 shadow-md shadow-brand-500/5'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#101726]/60'
              }`
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Analyst Session Profile footer */}
      <div className="p-4 border-t border-[#1a2336] bg-[#0c121e] flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-cyan-950/40 border border-cyan-800/60 flex items-center justify-center text-xs font-bold text-cyan-400">
          {userInitial}
        </div>
        <div className="truncate flex-1">
          <span className="block text-xs font-bold text-slate-200 truncate">
            {user?.user_id || 'Operator Session'}
          </span>
          <span className="block text-[10px] text-slate-500 truncate">
            ROLE: {(user?.role || 'operator').toUpperCase()}
          </span>
        </div>
      </div>
    </div>
  )
}
