import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface GrammarInfoProps {
  data: any
}

export default function GrammarInfo({ data }: GrammarInfoProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium">Initial Symbol</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-mono font-bold text-primary">{data.initial}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium">Terminals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {data.terminals.map((t: string) => (
              <span key={t} className="px-2 py-1 bg-primary/10 text-primary rounded text-sm font-mono">
                {t}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium">Non-terminals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {data.nonterminals.map((nt: string) => (
              <span key={nt} className="px-2 py-1 bg-accent/10 text-accent rounded text-sm font-mono">
                {nt}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
