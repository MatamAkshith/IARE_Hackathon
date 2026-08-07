import React from 'react'

/**
 * Campaign attribution status panel.
 * 
 * @param {Object} props
 * @param {Array} props.campaigns Campaigns stats list from dataset
 */
export default function CampaignOverview({ campaigns = [] }) {
  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl space-y-4">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Attribution Campaign Clusters</h3>
      </div>

      <div className="grid grid-cols-2 gap-3.5">
        {campaigns.map((item, idx) => (
          <div
            key={idx}
            className={`p-3.5 rounded-lg border text-left space-y-1 hover:-translate-y-0.5 transition-all duration-200 ${item.color}`}
          >
            <span className="block text-[9px] uppercase font-extrabold tracking-wider opacity-75">
              {item.label}
            </span>
            <span className="block text-2xl font-black font-mono tracking-tight text-slate-100">
              {item.count}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
