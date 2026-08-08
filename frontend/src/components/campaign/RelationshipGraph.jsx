import React, { useState, useEffect } from 'react'
import { getCampaignGraph } from '../../api/campaignService.js'

/**
 * Live SVG-based Threat Correlation Relationship Graph.
 * Visualizes shared attributes connecting campaigns, domains, and hosting nodes dynamically.
 *
 * @param {Object} props
 * @param {string} props.campaignId - Campaign database UUID/ID
 */
export default function RelationshipGraph({ campaignId }) {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hoveredNodeId, setHoveredNodeId] = useState(null)

  useEffect(() => {
    async function loadGraph() {
      if (!campaignId) return
      setLoading(true)
      setError(null)
      try {
        const data = await getCampaignGraph(campaignId)
        setGraphData(data)
      } catch (err) {
        console.error('Failed to load campaign graph:', err)
        setError('Graph visualization temporarily unavailable.')
      } finally {
        setLoading(false)
      }
    }
    loadGraph()
  }, [campaignId])

  if (loading) {
    return (
      <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl text-center text-xs text-slate-500 min-h-[300px] flex items-center justify-center">
        <div className="space-y-3">
          <svg className="animate-spin h-6 w-6 text-brand-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span>Compiling Campaign Topology...</span>
        </div>
      </div>
    )
  }

  if (error || !graphData.nodes || graphData.nodes.length === 0) {
    return (
      <div className="border border-[#1a2336] bg-[#090d16] p-6 rounded-xl text-center text-xs text-slate-500 min-h-[300px] flex items-center justify-center">
        <span>No topology graph data available for this campaign.</span>
      </div>
    )
  }

  // Layout calculations
  // Center is at (350, 180)
  const centerX = 350
  const centerY = 180

  // Filter indicator nodes (left side) and infrastructure nodes (right side)
  const indicatorNodes = graphData.nodes.filter(n => n.type === 'indicator')
  const infraNodes = graphData.nodes.filter(n => n.type !== 'indicator')

  // Calculate coordinates
  const mappedIndicatorNodes = indicatorNodes.map((n, idx) => {
    const total = indicatorNodes.length
    const startY = 60
    const endY = 320
    const step = total > 1 ? (endY - startY) / (total - 1) : 0
    return {
      id: n.id,
      label: n.label,
      x: 160,
      y: total > 1 ? startY + idx * step : centerY,
      type: n.type
    }
  })

  const mappedInfraNodes = infraNodes.map((n, idx) => {
    const total = infraNodes.length
    const startY = 50
    const endY = 330
    const step = total > 1 ? (endY - startY) / (total - 1) : 0
    return {
      id: n.id,
      label: n.label,
      x: 580,
      y: total > 1 ? startY + idx * step : centerY,
      type: n.type
    }
  })

  const allNodesMap = new Map()
  mappedIndicatorNodes.forEach(n => allNodesMap.set(n.id, n))
  mappedInfraNodes.forEach(n => allNodesMap.set(n.id, n))

  return (

    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl shadow-md space-y-4">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Threat Correlation Topology</h3>
      </div>

      {/* SVG Container wrapper with radial gradient */}
      <div 
        className="w-full overflow-x-auto select-none rounded-lg border border-[#141b2b]"
        style={{
          background: 'radial-gradient(circle at center, #0f172a 0%, #070b13 100%)'
        }}
      >
        <svg
          viewBox="0 0 740 360"
          className="w-full min-w-[600px] h-[360px] font-mono text-[9px]"
        >
          {/* Connector lines from center to indicator nodes */}
          {mappedIndicatorNodes.map((node, idx) => {
            const isHovered = hoveredNodeId === node.id
            const isAnyHovered = hoveredNodeId !== null
            const isHighlighted = hoveredNodeId === 'campaign' || isHovered
            const opacity = isAnyHovered ? (isHighlighted ? 1.0 : 0.25) : 0.6
            const strokeWidth = isHighlighted ? 2.5 : 1.5

            return (
              <line
                key={`line-ind-${idx}`}
                x1={centerX}
                y1={centerY}
                x2={node.x}
                y2={node.y}
                className="transition-all duration-200 stroke-rose-900"
                style={{
                  opacity,
                  strokeWidth,
                  strokeDasharray: isHighlighted ? 'none' : '4 3'
                }}
              />
            )
          })}

          {/* Connector lines from center to infra nodes */}
          {mappedInfraNodes.map((node, idx) => {
            const isHovered = hoveredNodeId === node.id
            const isAnyHovered = hoveredNodeId !== null
            const isHighlighted = hoveredNodeId === 'campaign' || isHovered
            const opacity = isAnyHovered ? (isHighlighted ? 1.0 : 0.25) : 0.6
            const strokeWidth = isHighlighted ? 2.5 : 1.5

            return (
              <line
                key={`line-inf-${idx}`}
                x1={centerX}
                y1={centerY}
                x2={node.x}
                y2={node.y}
                className="transition-all duration-200 stroke-brand-900"
                style={{
                  opacity,
                  strokeWidth
                }}
              />
            )
          })}

          {/* Draw extra edges defined in graphData if any (link indicator to infra) */}
          {(graphData.edges || []).map((edge, idx) => {
            const src = allNodesMap.get(edge.source)
            const tgt = allNodesMap.get(edge.target)
            if (!src || !tgt) return null

            const isAnyHovered = hoveredNodeId !== null
            const isHighlighted = hoveredNodeId === edge.source || hoveredNodeId === edge.target
            const opacity = isAnyHovered ? (isHighlighted ? 1.0 : 0.15) : 0.4
            const strokeWidth = isHighlighted ? 2 : 1

            return (
              <line
                key={`edge-${idx}`}
                x1={src.x}
                y1={src.y}
                x2={tgt.x}
                y2={tgt.y}
                className="transition-all duration-200 stroke-slate-700"
                style={{
                  opacity,
                  strokeWidth,
                  strokeDasharray: isHighlighted ? 'none' : '2 2'
                }}
              />
            )
          })}

          {/* Center Campaign Node */}
          <g 
            className="group cursor-pointer"
            onMouseEnter={() => setHoveredNodeId('campaign')}
            onMouseLeave={() => setHoveredNodeId(null)}
          >
            <circle
              cx={centerX}
              cy={centerY}
              r="24"
              className="fill-[#0f111a] stroke-rose-500 stroke-[2] hover:fill-rose-950/20 transition-all duration-200 shadow-xl"
              style={{
                filter: hoveredNodeId === 'campaign' ? 'drop-shadow(0 0 8px rgba(244, 63, 94, 0.6))' : 'none',
                opacity: hoveredNodeId !== null && hoveredNodeId !== 'campaign' ? 0.4 : 1.0
              }}
            />
            <text
              x={centerX}
              y={centerY - 32}
              textAnchor="middle"
              className="fill-rose-400 font-extrabold tracking-wider uppercase text-[9px]"
              style={{
                textShadow: '0 1px 2px rgba(0,0,0,0.9)',
                opacity: hoveredNodeId !== null && hoveredNodeId !== 'campaign' ? 0.4 : 1.0
              }}
            >
              Campaign Target
            </text>
            <text
              x={centerX}
              y={centerY + 3}
              textAnchor="middle"
              className="fill-slate-100 font-bold text-[8px]"
              style={{
                opacity: hoveredNodeId !== null && hoveredNodeId !== 'campaign' ? 0.4 : 1.0
              }}
            >
              {campaignId.substring(0, 8)}
            </text>
          </g>

          {/* Left Column Nodes (Indicators) */}
          {mappedIndicatorNodes.map((node, idx) => {
            const isHovered = hoveredNodeId === node.id
            const isAnyHovered = hoveredNodeId !== null
            const opacity = isAnyHovered ? (isHovered ? 1.0 : 0.4) : 1.0
            const strokeColor = isHovered ? '#f43f5e' : '#991b1b'
            const strokeWidth = isHovered ? 2.5 : 1.5
            const textWeight = isHovered ? 'bold' : 'normal'
            const textColor = isHovered ? '#ffffff' : '#D1D5DB'

            return (
              <g 
                key={`node-ind-${idx}`} 
                className="group cursor-pointer"
                onMouseEnter={() => setHoveredNodeId(node.id)}
                onMouseLeave={() => setHoveredNodeId(null)}
              >
                <title>{node.label}</title>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="12"
                  className="fill-[#0e1422] transition-all duration-200"
                  style={{
                    stroke: strokeColor,
                    strokeWidth,
                    opacity,
                    filter: isHovered ? 'drop-shadow(0 0 6px rgba(244, 63, 94, 0.5))' : 'none'
                  }}
                />
                <text
                  x={node.x - 22}
                  y={node.y + 3}
                  textAnchor="end"
                  className="transition-all duration-200 font-sans"
                  style={{
                    fill: textColor,
                    fontWeight: textWeight,
                    opacity,
                    textShadow: '0 1px 2px rgba(0,0,0,0.9)',
                    fontSize: '9px'
                  }}
                >
                  {node.label.length > 24 ? `${node.label.substring(0, 21)}...` : node.label}
                </text>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="3"
                  className="fill-rose-500 transition-all duration-200"
                  style={{
                    opacity,
                    transform: isHovered ? 'scale(1.25)' : 'none',
                    transformOrigin: `${node.x}px ${node.y}px`
                  }}
                />
              </g>
            )
          })}

          {/* Right Column Nodes (Infra nodes) */}
          {mappedInfraNodes.map((node, idx) => {
            const isHovered = hoveredNodeId === node.id
            const isAnyHovered = hoveredNodeId !== null
            const opacity = isAnyHovered ? (isHovered ? 1.0 : 0.4) : 1.0
            const strokeColor = isHovered ? '#38bdf8' : '#0369a1'
            const strokeWidth = isHovered ? 2.5 : 1.5
            const textWeight = isHovered ? 'bold' : 'normal'
            const textColor = isHovered ? '#ffffff' : '#D1D5DB'

            return (
              <g 
                key={`node-inf-${idx}`} 
                className="group cursor-pointer"
                onMouseEnter={() => setHoveredNodeId(node.id)}
                onMouseLeave={() => setHoveredNodeId(null)}
              >
                <title>{node.label}</title>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="12"
                  className="fill-[#0e1422] transition-all duration-200"
                  style={{
                    stroke: strokeColor,
                    strokeWidth,
                    opacity,
                    filter: isHovered ? 'drop-shadow(0 0 6px rgba(56, 189, 248, 0.5))' : 'none'
                  }}
                />
                <text
                  x={node.x + 22}
                  y={node.y + 3}
                  textAnchor="start"
                  className="transition-all duration-200 font-sans"
                  style={{
                    fill: textColor,
                    fontWeight: textWeight,
                    opacity,
                    textShadow: '0 1px 2px rgba(0,0,0,0.9)',
                    fontSize: '9px'
                  }}
                >
                  {node.label.length > 25 ? `${node.label.substring(0, 22)}...` : node.label}
                </text>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="3"
                  className="fill-brand-400 transition-all duration-200"
                  style={{
                    opacity,
                    transform: isHovered ? 'scale(1.25)' : 'none',
                    transformOrigin: `${node.x}px ${node.y}px`
                  }}
                />
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}

