"use client"

import { Input } from "@/components/ui/input"
import { useState } from "react"
import TraceTable from "@/components/tables/trace-table"
import DerivationTree from "@/components/derivation-tree"

interface ParseSectionProps {
  grammar: string
  buildData: any
  parseResult?: any
  onParseComplete: (data: any) => void
}

const ParseSection = ({ grammar, buildData, parseResult, onParseComplete }: ParseSectionProps) => {
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleParse = async () => {
    if (!input.trim() || !grammar) return

    setLoading(true)
    setError("")
    console.log("[v0] Sending parse request with input:", input)

    try {
      const response = await fetch("http://127.0.0.1:8000/parse", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ grammar, input }),
        mode: "cors",
      })

      console.log("[v0] Parse response status:", response.status)

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      console.log("[v0] Parse data received:", data)

      onParseComplete(data)
      setError("")
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error"
      console.error("[v0] Parse error:", errorMsg)
      setError(`Error: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <div>
          <label className="block text-lg font-bold text-gray-900 mb-2">Parse Input</label>
          <p className="text-sm text-gray-600 mb-3">Enter input tokens separated by spaces (e.g., c d d $)</p>
        </div>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your input tokens here..."
          className="font-mono"
          onKeyPress={(e) => e.key === "Enter" && handleParse()}
        />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          onClick={handleParse}
          disabled={!input.trim() || loading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded transition"
        >
          {loading ? "Parsing..." : "Parse"}
        </button>
      </div>

      {parseResult && (
        <div className="space-y-6">
          <div
            className={`p-4 rounded-lg ${parseResult.accepted ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}
          >
            <p className={`font-semibold ${parseResult.accepted ? "text-green-800" : "text-red-800"}`}>
              {parseResult.accepted ? "✓ Input accepted" : "✗ Input rejected"}
            </p>
          </div>
          <TraceTable trace={parseResult.trace} />
          {parseResult.tree && <DerivationTree tree={parseResult.tree} treeAscii={parseResult.tree_ascii} />}
        </div>
      )}
    </div>
  )
}

export default ParseSection
