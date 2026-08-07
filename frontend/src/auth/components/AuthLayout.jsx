import React from 'react';

/**
 * Enterprise SOC layout for ThreatLens authentication pages.
 * Displays a premium cyber-intelligence backdrop and handles responsive presentation.
 */
export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 flex items-center justify-center p-4 relative overflow-hidden font-sans select-none">
      {/* Decorative ambient background elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-cyan-900/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-blue-900/10 blur-[120px] pointer-events-none" />
      
      {/* Cyber grid overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[linear-gradient(to_right,#0891b2_1px,transparent_1px),linear-gradient(to_bottom,#0891b2_1px,transparent_1px)] bg-[size:4rem_4rem]"
      />

      {/* Main container */}
      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center z-10">
        
        {/* Left Side: Brand & Live Threat Monitoring Info Panel (Hidden on mobile) */}
        <div className="hidden lg:flex lg:col-span-6 flex-col justify-center space-y-8 pr-8 select-none">
          {/* Brand/Logo Header */}
          <div className="flex items-center space-x-3">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-[0_0_15px_rgba(6,182,212,0.4)] animate-pulse">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-cyan-200 to-cyan-400 bg-clip-text text-transparent">ThreatLens</span>
              <span className="text-[10px] block tracking-widest text-cyan-500 font-semibold uppercase leading-none mt-0.5">Enterprise SOC</span>
            </div>
          </div>

          {/* Value Prop & Dashboard Status Preview */}
          <div className="space-y-4">
            <h1 className="text-3xl font-extrabold tracking-tight text-white leading-tight">
              AI-Powered Phishing & Brand Impersonation Protection
            </h1>
            <p className="text-sm text-slate-400 leading-relaxed max-w-md">
              Secure enterprise operations against advanced phishing, replica domains, and rogue brand assets through our unified global threat intelligence scanner.
            </p>
          </div>

          {/* Live mock metrics cards for premium vibe */}
          <div className="grid grid-cols-2 gap-4 max-w-md">
            <div className="bg-[#090e1a]/60 border border-[#16223f] rounded-lg p-3 backdrop-blur-md">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Global Threats Analyzed</span>
              <span className="text-lg font-mono font-bold text-cyan-400">4,812,094</span>
              <span className="text-[10px] text-emerald-500 block mt-1 flex items-center font-medium">
                <svg className="w-3 h-3 mr-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                +24.8% (24h)
              </span>
            </div>
            <div className="bg-[#090e1a]/60 border border-[#16223f] rounded-lg p-3 backdrop-blur-md">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Active Takedown Requests</span>
              <span className="text-lg font-mono font-bold text-blue-400">142</span>
              <span className="text-[10px] text-slate-400 block mt-1 flex items-center">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mr-1.5 animate-ping" />
                8 processing now
              </span>
            </div>
          </div>

          {/* System status pill */}
          <div className="flex items-center space-x-2 bg-emerald-950/20 border border-emerald-900/30 w-fit px-3 py-1 rounded-full text-[11px] text-emerald-400 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>All System Nodes Nominal</span>
          </div>
        </div>

        {/* Right Side: The Login Card container */}
        <div className="lg:col-span-6 w-full flex justify-center">
          <div className="w-full max-w-md bg-[#090e1a]/40 border border-slate-800/60 rounded-2xl p-8 backdrop-blur-xl shadow-2xl relative">
            {/* Top accent line */}
            <div className="absolute top-0 left-0 right-0 h-[2px] rounded-t-2xl bg-gradient-to-r from-transparent via-cyan-500 to-blue-500" />
            
            {/* Mini logo display for mobile only */}
            <div className="flex lg:hidden items-center justify-between mb-8 select-none">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_10px_rgba(6,182,212,0.3)]">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <span className="text-lg font-bold tracking-tight text-white">ThreatLens</span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono">v1.2.4</span>
            </div>

            {children}
          </div>
        </div>

      </div>
    </div>
  );
}
