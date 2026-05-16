import { useEffect, useRef } from 'react'
import { Network } from 'vis-network/standalone/esm/vis-network'
import { DataSet } from 'vis-data/standalone/esm/vis-data'

// Stable color palette per domain. Add more as needed.
const DOMAIN_COLORS = {
  core:      '#7dd3fc',
  auth:      '#a78bfa',
  billing:   '#fbbf24',
  payments:  '#34d399',
  reporting: '#f472b6',
  legacy:    '#ef4444',
  unknown:   '#94a3b8',
}

export default function ArchitectureGraph({ graph, selected, onSelect }) {
  const containerRef = useRef(null)
  const networkRef = useRef(null)
  const datasetsRef = useRef({ nodes: null, edges: null })

  // Build the network once
  useEffect(() => {
    if (!containerRef.current || !graph) return

    const nodes = new DataSet(
      graph.nodes.map((n) => ({
        id: n.id,
        label: n.label,
        title: `${n.id}\n${n.loc} LOC · debt ${Math.round(n.debt_score || 0)}`,
        group: n.domain,
        value: Math.max(5, n.loc / 5),
        color: {
          background: DOMAIN_COLORS[n.domain] || DOMAIN_COLORS.unknown,
          border: '#0f172a',
        },
        font: { color: '#e2e8f0', size: 12 },
      }))
    )
    const edges = new DataSet(
      graph.edges.map((e, i) => ({
        id: `e${i}`,
        from: e.from,
        to: e.to,
        arrows: 'to',
        color: { color: 'rgba(148,163,184,0.35)', highlight: '#60a5fa' },
        width: 1,
      }))
    )
    datasetsRef.current = { nodes, edges }

    const network = new Network(
      containerRef.current,
      { nodes, edges },
      {
        layout: { improvedLayout: true },
        physics: {
          solver: 'forceAtlas2Based',
          forceAtlas2Based: { gravitationalConstant: -55, springLength: 110 },
          stabilization: { iterations: 200 },
        },
        interaction: { hover: true, tooltipDelay: 150 },
        nodes: {
          shape: 'dot',
          borderWidth: 2,
          scaling: { min: 8, max: 40 },
        },
      }
    )
    network.on('selectNode', (params) => {
      if (params.nodes[0]) onSelect(params.nodes[0])
    })
    networkRef.current = network

    return () => {
      network.destroy()
      networkRef.current = null
    }
  }, [graph])

  // Highlight selected node + neighborhood
  useEffect(() => {
    const net = networkRef.current
    const { nodes, edges } = datasetsRef.current
    if (!net || !nodes || !edges || !selected) return

    net.selectNodes([selected])
    net.focus(selected, { scale: 1.2, animation: { duration: 400 } })

    // dim others, brighten neighbors
    const connected = new Set([selected, ...net.getConnectedNodes(selected)])
    nodes.update(
      graph.nodes.map((n) => ({
        id: n.id,
        color: {
          background: connected.has(n.id)
            ? (DOMAIN_COLORS[n.domain] || DOMAIN_COLORS.unknown)
            : '#1e293b',
          border: connected.has(n.id) ? '#f8fafc' : '#0f172a',
        },
        font: { color: connected.has(n.id) ? '#f8fafc' : '#475569', size: 12 },
      }))
    )
  }, [selected, graph])

  return (
    <div className="graph-wrap">
      <div className="graph-legend">
        {Object.entries(DOMAIN_COLORS).map(([d, c]) => (
          <span key={d} className="legend-item">
            <span className="legend-dot" style={{ background: c }} />{d}
          </span>
        ))}
      </div>
      <div ref={containerRef} className="graph-canvas" />
    </div>
  )
}
