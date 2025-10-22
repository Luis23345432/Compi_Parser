"use client"

import { Textarea } from "@/components/ui/textarea"
import { useState } from "react"
import GrammarInfo from "@/components/grammar-info"
import StatesTable from "@/components/tables/states-table"
import TablesDisplay from "@/components/tables/tables-display"
import ClosureTable from "@/components/tables/closure-table"

interface BuildSectionProps {
  grammar: string
  setGrammar: (grammar: string) => void
  onBuildComplete: (grammar: string, data: any) => void
  buildResult?: any
}

const BuildSection = ({ grammar, setGrammar, onBuildComplete, buildResult }: BuildSectionProps) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleBuild = async () => {
    if (!grammar.trim()) return

    setLoading(true)
    setError("")
    console.log("[v0] Sending build request with grammar:", grammar)

    try {
      const response = await fetch("http://127.0.0.1:8000/build", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ grammar }),
        mode: "cors",
      })

      console.log("[v0] Build response status:", response.status)

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      console.log("[v0] Build data received:", data)

      onBuildComplete(grammar, data)
      setError("")
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error"
      console.error("[v0] Build error:", errorMsg)
      setError(`Error: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <div>
          <label className="text-lg font-bold text-gray-900">Grammar Input</label>
          <p className="text-sm text-gray-600 mt-2">Enter your grammar rules (one per line, format: A → B C)</p>
        </div>
        <Textarea
          value={grammar}
          onChange={(e) => setGrammar(e.target.value)}
          placeholder="Enter your grammar rules here..."
          className="font-mono min-h-32"
        />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          onClick={handleBuild}
          disabled={!grammar.trim() || loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded transition"
        >
          {loading ? "Building..." : "Build"}
        </button>
      </div>

      {buildResult && (
        <div className="space-y-6">
          <GrammarInfo data={buildResult} />
          {buildResult.closure_table && <ClosureTable closureTable={buildResult.closure_table} />}
          <StatesTable states={buildResult.states} />
          <TablesDisplay tables={buildResult.tables} />
        </div>
      )}
    </div>
  )
}

export default BuildSection
