import { useEffect, useRef } from 'react'
import { Network } from 'vis-network/standalone/esm/vis-network'
import { DataSet } from 'vis-data/standalone/esm/vis-data'

// Warm, muted domain colors - architectural and elegant
const DOMAIN_COLORS = {
  core:      '#8b9aab',  // steel blue
  auth:      '#9ca896',  // sage green
  billing:   '#d4a574',  // warm bronze
  payments:  '#7a9b7e',  // muted green
  reporting: '#b8956a',  // dusty bronze
  legacy:    '#b87070',  // muted red
  unknown:   '#8a8379',  // warm gray
}

export default function ArchitectureGraph({ graph, selected, onSelect }) {
  const containerRef = useRef(null)
  const networkRef = useRef(null)
  const datasetsRef = useRef({ nodes: null, edges: null })

  // Build the network once with premium styling
  useEffect(() => {
    if (!containerRef.current || !graph) return

    const nodes = new DataSet(
      graph.nodes.map((n) => ({
        id: n.id,
        label: n.label,
        title: `${n.id}\n${n.loc} LOC · debt ${Math.round(n.debt_score || 0)}`,
        group: n.domain,
        value: Math.max(8, n.loc / 4),
        color: {
          background: DOMAIN_COLORS[n.domain] || DOMAIN_COLORS.unknown,
          border: 'rgba(245, 241, 237, 0.15)',
          highlight: {
            background: DOMAIN_COLORS[n.domain] || DOMAIN_COLORS.unknown,
            border: 'rgba(245, 241, 237, 0.4)',
          },
          hover: {
            background: DOMAIN_COLORS[n.domain] || DOMAIN_COLORS.unknown,
            border: 'rgba(245, 241, 237, 0.3)',
          }
        },
        font: {
          color: '#f5f1ed',
          size: 13,
          face: '-apple-system, BlinkMacSystemFont, Inter, SF Pro Display, sans-serif',
        },
        shadow: {
          enabled: true,
          color: 'rgba(0, 0, 0, 0.2)',
          size: 8,
          x: 0,
          y: 2,
        },
      }))
    )
    
    const edges = new DataSet(
      graph.edges.map((e, i) => ({
        id: `e${i}`,
        from: e.from,
        to: e.to,
        arrows: {
          to: {
            enabled: true,
            scaleFactor: 0.6,
          }
        },
        color: {
          color: 'rgba(138, 131, 121, 0.15)',
          highlight: 'rgba(156, 168, 150, 0.5)',
          hover: 'rgba(156, 168, 150, 0.3)',
        },
        width: 1,
        smooth: {
          enabled: true,
          type: 'continuous',
          roundness: 0.2,
        },
      }))
    )
    datasetsRef.current = { nodes, edges }

    const network = new Network(
      containerRef.current,
      { nodes, edges },
      {
        layout: {
          improvedLayout: true,
          randomSeed: 42,
        },
        physics: {
          solver: 'forceAtlas2Based',
          forceAtlas2Based: {
            gravitationalConstant: -65,
            springLength: 140,
            springConstant: 0.08,
            damping: 0.6,
            avoidOverlap: 0.8,
          },
          stabilization: {
            iterations: 250,
            updateInterval: 25,
          },
        },
        interaction: {
          hover: true,
          tooltipDelay: 200,
          navigationButtons: false,
          keyboard: false,
        },
        nodes: {
          shape: 'dot',
          borderWidth: 2,
          borderWidthSelected: 3,
          scaling: {
            min: 12,
            max: 45,
          },
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
  }, [graph, onSelect])

  // Focus mode: elegant highlighting with smooth transitions
  useEffect(() => {
    const net = networkRef.current
    const { nodes, edges } = datasetsRef.current
    if (!net || !nodes || !edges || !selected) return

    // Smooth focus animation
    net.selectNodes([selected])
    net.focus(selected, {
      scale: 1.3,
      animation: {
        duration: 600,
        easingFunction: 'easeInOutCubic'
      }
    })

    // Get connected nodes for context
    const connected = new Set([selected, ...net.getConnectedNodes(selected)])
    
    // Update nodes with elegant fade effect
    nodes.update(
      graph.nodes.map((n) => {
        const isConnected = connected.has(n.id)
        const isSelected = n.id === selected
        const domainColor = DOMAIN_COLORS[n.domain] || DOMAIN_COLORS.unknown
        
        return {
          id: n.id,
          color: {
            background: isConnected ? domainColor : 'rgba(37, 34, 32, 0.4)',
            border: isSelected
              ? 'rgba(245, 241, 237, 0.6)'
              : isConnected
                ? 'rgba(245, 241, 237, 0.25)'
                : 'rgba(245, 241, 237, 0.08)',
            highlight: {
              background: domainColor,
              border: 'rgba(245, 241, 237, 0.5)',
            }
          },
          font: {
            color: isConnected ? '#f5f1ed' : 'rgba(138, 131, 121, 0.5)',
            size: isSelected ? 14 : 13,
          },
          shadow: isSelected ? {
            enabled: true,
            color: `${domainColor}40`,
            size: 16,
            x: 0,
            y: 3,
          } : {
            enabled: isConnected,
            color: 'rgba(0, 0, 0, 0.2)',
            size: 8,
            x: 0,
            y: 2,
          },
        }
      })
    )
    
    // Update edges with subtle highlighting
    edges.update(
      graph.edges.map((e, i) => {
        const isConnected = connected.has(e.from) || connected.has(e.to)
        return {
          id: `e${i}`,
          color: {
            color: isConnected
              ? 'rgba(156, 168, 150, 0.35)'
              : 'rgba(138, 131, 121, 0.08)',
            highlight: 'rgba(156, 168, 150, 0.6)',
          },
          width: isConnected ? 1.5 : 1,
        }
      })
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
