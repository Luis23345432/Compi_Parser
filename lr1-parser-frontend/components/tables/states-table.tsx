"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import StatesGraph from "./states-graph"

interface StatesTableProps {
  states: any[]
}

export default function StatesTable({ states }: StatesTableProps) {
  const [viewMode, setViewMode] = useState<"table" | "graph">("table")

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>LR(1) States</CardTitle>
            <CardDescription>Canonical collection of LR(1) items</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant={viewMode === "table" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("table")}
            >
              Table
            </Button>
            <Button
              variant={viewMode === "graph" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("graph")}
            >
              Graph
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {viewMode === "table" ? (
          <ScrollArea className="w-full">
            <div className="space-y-4">
              {states.map((state) => (
                <div key={state.id} className="border rounded-lg p-4 bg-card/50">
                  <div className="font-mono font-bold mb-3 text-primary">State {state.id}</div>
                  <div className="space-y-2 mb-4">
                    {state.items.map((item: any, idx: number) => (
                      <div key={idx} className="text-sm font-mono text-foreground/80">
                        {item.text}
                      </div>
                    ))}
                  </div>
                  {state.transitions.length > 0 && (
                    <div className="pt-3 border-t">
                      <div className="text-xs font-semibold text-muted-foreground mb-2">Transitions:</div>
                      <div className="flex flex-wrap gap-2">
                        {state.transitions.map((trans: any, idx: number) => (
                          <span key={idx} className="px-2 py-1 bg-primary/10 text-primary rounded text-xs font-mono">
                            {trans.symbol} → {trans.to}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        ) : (
          <StatesGraph states={states} />
        )}
      </CardContent>
    </Card>
  )
}
