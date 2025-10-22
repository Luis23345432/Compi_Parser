import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"

interface TablesDisplayProps {
  tables: any
}

export default function TablesDisplay({ tables }: TablesDisplayProps) {
  const actionTable = tables.action
  const gotoTable = tables.goto
  const terminals = tables.terminals
  const nonterminals = tables.nonterminals

  return (
    <Card>
      <CardHeader>
        <CardTitle>Parsing Tables</CardTitle>
        <CardDescription>ACTION and GOTO tables for the LR(1) parser</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="action" className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="action">ACTION Table</TabsTrigger>
            <TabsTrigger value="goto">GOTO Table</TabsTrigger>
          </TabsList>

          <TabsContent value="action" className="mt-4">
            <ScrollArea className="w-full">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b bg-primary/10">
                    <th className="px-4 py-2 text-left font-semibold text-primary">State</th>
                    {terminals.map((term: string) => (
                      <th key={term} className="px-4 py-2 text-center font-semibold text-primary">
                        {term}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(actionTable).map(([state, actions]: [string, any]) => (
                    <tr key={state} className="border-b hover:bg-muted/50">
                      <td className="px-4 py-2 font-mono font-bold text-foreground">{state}</td>
                      {terminals.map((term: string) => {
                        const action = actions[term]
                        return (
                          <td key={`${state}-${term}`} className="px-4 py-2 text-center font-mono text-sm">
                            {action ? (
                              <span
                                className={`px-2 py-1 rounded text-xs font-semibold ${
                                  action.type === "shift"
                                    ? "bg-blue-500/20 text-blue-600"
                                    : action.type === "reduce"
                                      ? "bg-orange-500/20 text-orange-600"
                                      : "bg-green-500/20 text-green-600"
                                }`}
                              >
                                {action.type === "shift" && `s${action.to}`}
                                {action.type === "reduce" && `r${action.lhs}`}
                                {action.type === "accept" && "acc"}
                              </span>
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="goto" className="mt-4">
            <ScrollArea className="w-full">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b bg-accent/10">
                    <th className="px-4 py-2 text-left font-semibold text-accent">State</th>
                    {nonterminals.map((nt: string) => (
                      <th key={nt} className="px-4 py-2 text-center font-semibold text-accent">
                        {nt}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(gotoTable).map(([state, gotos]: [string, any]) => (
                    <tr key={state} className="border-b hover:bg-muted/50">
                      <td className="px-4 py-2 font-mono font-bold text-foreground">{state}</td>
                      {nonterminals.map((nt: string) => {
                        const gotoState = (gotos as any)[nt]
                        return (
                          <td key={`${state}-${nt}`} className="px-4 py-2 text-center font-mono text-sm">
                            {gotoState !== undefined ? (
                              <span className="px-2 py-1 rounded text-xs font-semibold bg-accent/20 text-accent">
                                {gotoState}
                              </span>
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
