"use client"

import { useState, useEffect } from "react"
import BuildSection from "@/components/build-section"
import ParseSection from "@/components/parse-section"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function Home() {
  const [grammar, setGrammar] = useState<string>("")
  const [buildData, setBuildData] = useState<any>(null)
  const [parseResult, setParseResult] = useState<any>(null)

  useEffect(() => {
    const saved = localStorage.getItem("lr1_grammar")
    const savedBuild = localStorage.getItem("lr1_build_data")
    const savedParse = localStorage.getItem("lr1_parse_result")
    if (saved) setGrammar(saved)
    if (savedBuild) setBuildData(JSON.parse(savedBuild))
    if (savedParse) setParseResult(JSON.parse(savedParse))
  }, [])

  const handleBuildComplete = (newGrammar: string, data: any) => {
    setGrammar(newGrammar)
    setBuildData(data)
    localStorage.setItem("lr1_grammar", newGrammar)
    localStorage.setItem("lr1_build_data", JSON.stringify(data))
  }

  const handleParseComplete = (data: any) => {
    setParseResult(data)
    localStorage.setItem("lr1_parse_result", JSON.stringify(data))
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">LR(1) Parser</h1>
          <p className="text-muted-foreground">Build and analyze LR(1) parsing tables</p>
        </div>

        <Tabs defaultValue="build" className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="build">Build Grammar</TabsTrigger>
            <TabsTrigger value="parse" disabled={!buildData}>
              Parse Input
            </TabsTrigger>
          </TabsList>

          <TabsContent value="build" className="mt-6">
            <BuildSection
              grammar={grammar}
              setGrammar={setGrammar}
              onBuildComplete={handleBuildComplete}
              buildResult={buildData}
            />
          </TabsContent>

          <TabsContent value="parse" className="mt-6">
            {buildData && (
              <ParseSection
                grammar={grammar}
                buildData={buildData}
                parseResult={parseResult}
                onParseComplete={handleParseComplete}
              />
            )}
          </TabsContent>
        </Tabs>
      </div>
    </main>
  )
}
