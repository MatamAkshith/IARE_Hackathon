import React, { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'

/**
 * Main application shell composing Sidebar navigation panel, Topbar context,
 * and page rendering outlet. Manages mobile-responsive navigation menus.
 */
export default function DashboardLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => setMobileMenuOpen(prev => !prev)
  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <div className="flex h-screen bg-[#070b13] text-[#f1f5f9] overflow-hidden">
      {/* 1. Desktop Sidebar (Permanent aside block for wider resolutions) */}
      <aside className="hidden md:block w-64 flex-shrink-0 h-full">
        <Sidebar />
      </aside>

      {/* 2. Mobile Sidebar Overlay Drawer (Toggled via hamburger click) */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-30 flex">
          {/* Backdrop layer */}
          <div
            onClick={closeMobileMenu}
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity duration-300"
            aria-hidden="true"
          />

          {/* Drawer sheet */}
          <div className="relative w-64 max-w-xs flex-1 flex flex-col h-full z-40 animate-slide-in">
            <Sidebar onItemClick={closeMobileMenu} />
          </div>
        </div>
      )}

      {/* 3. Main Dashboard Window container */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <Topbar onMenuToggle={toggleMobileMenu} />
        
        {/* Scrollable Main content box */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
