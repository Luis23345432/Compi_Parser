"use client"

import type React from "react"

import { useMemo, useRef, useState } from "react"

interface StatesGraphProps {
  states: any[]
}

export default function StatesGraph({ states }: StatesGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isPanning, setIsPanning] = useState(false)
  const [panStart, setPanStart] = useState({ x: 0, y: 0 })

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(3, prev + 0.2))
  }

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(0.5, prev - 0.2))
  }

  const handleResetZoom = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  const { nodes, edges } = useMemo(() => {
    if (!states || !Array.isArray(states) || states.length === 0) {
      return { nodes: [], edges: [] }
    }

    const cols = Math.ceil(Math.sqrt(states.length))
    const nodeWidth = 280
    const spacingX = 380
    const spacingY = 300

    const nodes = states.map((state, idx) => {
      const col = idx % cols
      const row = Math.floor(idx / cols)
      const x = col * spacingX + 50
      const y = row * spacingY + 50

      const items = state.items || []
      const itemsText = items.map((item: any) => {
        if (typeof item === "string") return item
        return `${item.lhs} -> ${item.rhs.join(" ")}, ${item.lookahead}`
      })

      const itemHeight = Math.max(120, items.length * 18 + 40)

      const transitions = state.transitions || []
      const transitionMap = new Map<string, number>()
      transitions.forEach((trans: any) => {
        transitionMap.set(trans.symbol, trans.to)
      })
      const transitionsText = Array.from(transitionMap.entries())
        .map(([symbol, to]) => `${symbol} → ${to}`)
        .join(", ")

      return {
        id: state.id,
        items: itemsText,
        transitions: transitionsText,
        x,
        y,
        width: nodeWidth,
        height: itemHeight,
        isInitial: state.id === 0,
      }
    })

    const edgeMap = new Map<string, string[]>()
    states.forEach((state) => {
      const transitions = state.transitions || []
      transitions.forEach((trans: any) => {
        const key = `${state.id}-${trans.to}`
        if (!edgeMap.has(key)) {
          edgeMap.set(key, [])
        }
        edgeMap.get(key)!.push(trans.symbol)
      })
    })

    const edges = Array.from(edgeMap.entries()).map(([key, symbols]) => {
      const [from, to] = key.split("-").map(Number)
      return { from, to, symbols: symbols.join(", ") }
    })

    return { nodes, edges }
  }, [states])

  if (nodes.length === 0) {
    return <div className="w-full border rounded-lg bg-white p-4 text-center text-gray-500">No states to display</div>
  }

  const nodeMap = new Map(nodes.map((n) => [n.id, n]))

  const getEdgePath = (fromNode: any, toNode: any) => {
    const fromCenterX = fromNode.x + fromNode.width / 2
    const fromCenterY = fromNode.y + fromNode.height / 2
    const toCenterX = toNode.x + toNode.width / 2
    const toCenterY = toNode.y + toNode.height / 2

    const dx = toCenterX - fromCenterX
    const dy = toCenterY - fromCenterY
    const distance = Math.sqrt(dx * dx + dy * dy)

    if (distance === 0) return null

    const fromX = fromCenterX + (dx / distance) * (fromNode.width / 2)
    const fromY = fromCenterY + (dy / distance) * (fromNode.height / 2)
    const toX = toCenterX - (dx / distance) * (toNode.width / 2)
    const toY = toCenterY - (dy / distance) * (toNode.height / 2)

    const midX = (fromX + toX) / 2
    const midY = (fromY + toY) / 2
    const perpX = (-dy / distance) * 60
    const perpY = (dx / distance) * 60

    return {
      path: `M ${fromX} ${fromY} Q ${midX + perpX} ${midY + perpY} ${toX} ${toY}`,
      labelX: midX + perpX,
      labelY: midY + perpY,
    }
  }

  const handleMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
    if (e.button === 0) {
      setIsPanning(true)
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
    }
  }

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      })
    }
  }

  const handleMouseUp = () => {
    setIsPanning(false)
  }

  const maxCol = Math.ceil(Math.sqrt(nodes.length))
  const maxRow = Math.ceil(nodes.length / maxCol)
  const svgWidth = Math.max(1000, maxCol * 380 + 100)
  const svgHeight = Math.max(600, maxRow * 300 + 200)

  return (
    <div className="w-full border rounded-lg bg-white overflow-hidden">
      <div className="flex items-center justify-between p-2 bg-gray-50 border-b">
        <div className="text-xs text-gray-500">Click and drag to pan</div>
        <div className="flex gap-2">
          <button
            onClick={handleZoomOut}
            className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 rounded border border-gray-300 transition-colors"
            title="Zoom out"
          >
            −
          </button>
          <span className="px-2 py-1 text-xs bg-gray-100 rounded border border-gray-300 min-w-12 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 rounded border border-gray-300 transition-colors"
            title="Zoom in"
          >
            +
          </button>
          <button
            onClick={handleResetZoom}
            className="px-2 py-1 text-xs bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded border border-indigo-300 transition-colors"
            title="Reset zoom and pan"
          >
            Reset
          </button>
        </div>
      </div>
      <svg
        ref={svgRef}
        width={svgWidth}
        height={svgHeight}
        className="min-w-full cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
              <polygon points="0 0, 10 3, 0 6" fill="#6366f1" />
            </marker>
          </defs>

          {/* Draw edges - simple lines without label boxes */}
          {edges.map((edge, idx) => {
            const fromNode = nodeMap.get(edge.from)
            const toNode = nodeMap.get(edge.to)
            if (!fromNode || !toNode) return null

            const edgePath = getEdgePath(fromNode, toNode)
            if (!edgePath) return null

            const { path } = edgePath

            return (
              <path
                key={`edge-${idx}`}
                d={path}
                stroke="#6366f1"
                strokeWidth="2"
                fill="none"
                markerEnd="url(#arrowhead)"
              />
            )
          })}

          {/* Draw nodes */}
          {nodes.map((node) => (
            <g key={`node-${node.id}`}>
              <rect
                x={node.x}
                y={node.y}
                width={node.width}
                height={node.height}
                fill={node.isInitial ? "#dbeafe" : "#f3f4f6"}
                stroke={node.isInitial ? "#3b82f6" : "#9ca3af"}
                strokeWidth="2"
                rx="4"
              />
              <text x={node.x + 10} y={node.y + 18} className="text-xs font-bold fill-gray-900">
                State {node.id}
              </text>
              <line
                x1={node.x}
                y1={node.y + 25}
                x2={node.x + node.width}
                y2={node.y + 25}
                stroke="#d1d5db"
                strokeWidth="1"
              />
              <foreignObject x={node.x + 5} y={node.y + 30} width={node.width - 10} height={node.height - 35}>
                <div className="text-xs text-gray-700 overflow-y-auto h-full">
                  {node.items.map((item: string, i: number) => (
                    <div key={i} className="whitespace-nowrap text-ellipsis overflow-hidden py-0.5">
                      {item}
                    </div>
                  ))}
                </div>
              </foreignObject>

              <text
                x={node.x + node.width / 2}
                y={node.y + node.height + 20}
                textAnchor="middle"
                className="text-xs font-semibold fill-indigo-600"
              >
                Transitions: {node.transitions}
              </text>
            </g>
          ))}
        </g>
      </svg>
    </div>
  )
}
