import React from 'react'

/**
 * Static SVG-based Relationship Correlation Graph.
 * Visualizes shared attributes connecting CozyBear campaigns, domains, and hosting nodes.
 */
export default function RelationshipGraph() {
  // Center: (400, 220)
  const centerNode = { x: 400, y: 220, label: 'CAMP-2026-004 CozyBear', color: 'fill-[#0e1726] stroke-rose-500' }

  // Left column: CozyBear lookalike domains
  const domainNodes = [
    { x: 140, y: 80, label: 'secure-microsoft...com', val: 'Domain 1' },
    { x: 140, y: 160, label: 'office365-security...net', val: 'Domain 2' },
    { x: 140, y: 240, label: 'microsoft-login...live', val: 'Domain 3' },
    { x: 140, y: 320, label: 'login-update...co', val: 'Domain 4' }
  ]

  // Right column: shared infrastructure elements
  const infraNodes = [
    { x: 660, y: 60, label: 'IP: 185.230.125.44', val: 'IP Address' },
    { x: 660, y: 120, label: 'SSL: Self-Signed CA', val: 'SSL Certificate' },
    { x: 660, y: 180, label: 'WHOIS: NameCheap Privacy', val: 'WHOIS Owner' },
    { x: 660, y: 240, label: 'Host: GlobalHost Corp', val: 'Hosting Provider' },
    { x: 660, y: 300, label: 'DNS: ns1.fakehost.com', val: 'Nameservers' },
    { x: 660, y: 360, label: 'ASN: AS41235 Network', val: 'ASN Registry' }
  ]

  return (
    <div className="border border-[#1a2336] bg-[#090d16] p-5 rounded-xl shadow-md space-y-4">
      <div className="flex items-center gap-2 border-b border-[#1a2336]/60 pb-3">
        <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
        </svg>
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Threat Correlation Topology</h3>
      </div>

      {/* SVG Container wrapper */}
      <div className="w-full overflow-x-auto select-none bg-[#070b13]/60 rounded-lg border border-[#141b2b]">
        <svg
          viewBox="0 0 800 400"
          className="w-full min-w-[650px] h-[340px] md:h-[400px] font-mono text-[10px]"
        >
          {/* Connector lines to left column */}
          {domainNodes.map((node, idx) => (
            <g key={`line-dom-${idx}`}>
              <line
                x1={centerNode.x}
                y1={centerNode.y}
                x2={node.x}
                y2={node.y}
                className="stroke-rose-900/60 stroke-[1.5]"
                strokeDasharray="4 3"
              />
            </g>
          ))}

          {/* Connector lines to right column */}
          {infraNodes.map((node, idx) => (
            <g key={`line-infra-${idx}`}>
              <line
                x1={centerNode.x}
                y1={centerNode.y}
                x2={node.x}
                y2={node.y}
                className="stroke-brand-900/60 stroke-[1.5]"
              />
            </g>
          ))}

          {/* Center CozyBear Node */}
          <g className="group cursor-pointer">
            <circle
              cx={centerNode.x}
              cy={centerNode.y}
              r="28"
              className={`${centerNode.color} stroke-[2.5] fill-[#0f111a] hover:fill-rose-950/20 transition-colors duration-200 shadow-xl`}
            />
            <text
              x={centerNode.x}
              y={centerNode.y - 36}
              textAnchor="middle"
              className="fill-rose-400 font-extrabold tracking-wider uppercase text-[10px]"
            >
              COZYBEAR CAMPAIGN
            </text>
            <text
              x={centerNode.x}
              y={centerNode.y + 4}
              textAnchor="middle"
              className="fill-slate-100 font-bold text-[9px]"
            >
              CAMP-004
            </text>
          </g>

          {/* Left Column Nodes (Lookalike Domains) */}
          {domainNodes.map((node, idx) => (
            <g key={`node-dom-${idx}`} className="group cursor-pointer">
              <circle
                cx={node.x}
                cy={node.y}
                r="16"
                className="fill-[#0e1422] stroke-rose-800/80 stroke-2 hover:stroke-rose-500 hover:fill-rose-950/20 transition-all duration-200"
              />
              <text
                x={node.x - 24}
                y={node.y + 4}
                textAnchor="end"
                className="fill-slate-300 font-semibold hover:fill-slate-100 transition-colors"
              >
                {node.label}
              </text>
              <circle
                cx={node.x}
                cy={node.y}
                r="4"
                className="fill-rose-500 group-hover:scale-125 transition-transform"
              />
            </g>
          ))}

          {/* Right Column Nodes (Shared Infrastructure) */}
          {infraNodes.map((node, idx) => (
            <g key={`node-infra-${idx}`} className="group cursor-pointer">
              <circle
                cx={node.x}
                cy={node.y}
                r="16"
                className="fill-[#0e1422] stroke-brand-800/80 stroke-2 hover:stroke-brand-400 hover:fill-brand-950/20 transition-all duration-200"
              />
              <text
                x={node.x + 24}
                y={node.y + 4}
                textAnchor="start"
                className="fill-slate-300 font-semibold hover:fill-slate-100 transition-colors"
              >
                {node.label}
              </text>
              <circle
                cx={node.x}
                cy={node.y}
                r="4"
                className="fill-brand-400 group-hover:scale-125 transition-transform"
              />
            </g>
          ))}
        </svg>
      </div>
    </div>
  )
}
