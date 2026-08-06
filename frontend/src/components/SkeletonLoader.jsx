import React from 'react'

/**
 * Premium pulsing loading skeleton cards.
 */
export default function SkeletonLoader() {
  return (
    <div className="space-y-6 w-full animate-pulse">
      {/* Header Skeleton */}
      <div className="space-y-2">
        <div className="h-6 w-1/3 bg-slate-800 rounded" />
        <div className="h-3.5 w-1/2 bg-slate-850 rounded" />
      </div>

      {/* Grid segments skeletons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="border border-slate-800 bg-[#090d16]/60 p-5 rounded-xl h-44 space-y-4">
          <div className="h-4 w-1/4 bg-slate-800 rounded" />
          <div className="h-8 w-1/2 bg-slate-800 rounded" />
          <div className="h-3 w-3/4 bg-slate-850 rounded" />
        </div>
        <div className="border border-slate-800 bg-[#090d16]/60 p-5 rounded-xl h-44 space-y-4">
          <div className="h-4 w-1/4 bg-slate-800 rounded" />
          <div className="h-8 w-1/2 bg-slate-800 rounded" />
          <div className="h-3 w-3/4 bg-slate-850 rounded" />
        </div>
        <div className="border border-slate-800 bg-[#090d16]/60 p-5 rounded-xl h-44 space-y-4">
          <div className="h-4 w-1/4 bg-slate-800 rounded" />
          <div className="h-8 w-1/2 bg-slate-800 rounded" />
          <div className="h-3 w-3/4 bg-slate-850 rounded" />
        </div>
      </div>

      {/* Main content split panel skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 border border-slate-800 bg-[#090d16]/60 p-6 rounded-xl h-96 space-y-4">
          <div className="h-5 w-1/5 bg-slate-800 rounded" />
          <div className="space-y-3 pt-4">
            <div className="h-4 w-full bg-slate-850 rounded" />
            <div className="h-4 w-full bg-slate-850 rounded" />
            <div className="h-4 w-full bg-slate-850 rounded" />
            <div className="h-4 w-full bg-slate-850 rounded" />
          </div>
        </div>
        <div className="border border-slate-800 bg-[#090d16]/60 p-6 rounded-xl h-96 space-y-4">
          <div className="h-5 w-1/3 bg-slate-800 rounded" />
          <div className="space-y-3 pt-4">
            <div className="h-4 w-full bg-slate-850 rounded" />
            <div className="h-4 w-full bg-slate-850 rounded" />
            <div className="h-4 w-full bg-slate-850 rounded" />
          </div>
        </div>
      </div>
    </div>
  )
}
