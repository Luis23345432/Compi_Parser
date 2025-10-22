import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"

interface ClosureTableProps {
  closureTable: any[]
}

export default function ClosureTable({ closureTable }: ClosureTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>LR(1) Closure Table</CardTitle>
        <CardDescription>Kernel items and their closures for each state</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="w-full">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-primary/10 border-b-2 border-primary">
                <th className="border px-3 py-2 text-left font-semibold text-primary">Goto</th>
                <th className="border px-3 py-2 text-left font-semibold text-primary">Kernel</th>
                <th className="border px-3 py-2 text-left font-semibold text-primary">State</th>
                <th className="border px-3 py-2 text-left font-semibold text-primary">Closure</th>
              </tr>
            </thead>
            <tbody>
              {closureTable.map((row) => (
                <tr key={row.id} className="border-b hover:bg-muted/50">
                  {/* Goto column */}
                  <td className="border px-3 py-2 font-mono text-xs">
                    <div className="space-y-1">
                      {row.transitions.map((trans: any, idx: number) => (
                        <div key={idx} className="text-foreground/70">
                          goto({row.id}, {trans.symbol})
                        </div>
                      ))}
                    </div>
                  </td>

                  {/* Kernel column */}
                  <td className="border px-3 py-2 font-mono text-xs">
                    <div className="space-y-1">
                      {row.kernel.map((item: any, idx: number) => (
                        <div
                          key={idx}
                          className="text-foreground/80 bg-green-50 dark:bg-green-950/20 px-2 py-1 rounded"
                        >
                          {item.text}
                        </div>
                      ))}
                    </div>
                  </td>

                  {/* State column */}
                  <td className="border px-3 py-2 font-mono font-bold text-center">
                    <div className="bg-blue-100 dark:bg-blue-950/30 px-3 py-1 rounded inline-block text-primary">
                      {row.id}
                    </div>
                  </td>

                  {/* Closure column */}
                  <td className="border px-3 py-2 font-mono text-xs">
                    <div className="space-y-1">
                      {row.closure.map((item: any, idx: number) => (
                        <div key={idx} className="text-foreground/70">
                          {item.text}
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
