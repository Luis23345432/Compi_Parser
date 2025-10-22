import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"

interface TraceTableProps {
  trace: any[]
}

export default function TraceTable({ trace }: TraceTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Parse Trace</CardTitle>
        <CardDescription>Step-by-step parsing execution</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="w-full">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b bg-primary/10">
                <th className="px-4 py-2 text-left font-semibold text-primary">Step</th>
                <th className="px-4 py-2 text-left font-semibold text-primary">Stack States</th>
                <th className="px-4 py-2 text-left font-semibold text-primary">Stack Symbols</th>
                <th className="px-4 py-2 text-left font-semibold text-primary">Input</th>
                <th className="px-4 py-2 text-left font-semibold text-primary">Action</th>
              </tr>
            </thead>
            <tbody>
              {trace.map((step, idx) => (
                <tr key={idx} className="border-b hover:bg-muted/50">
                  <td className="px-4 py-2 font-mono font-bold text-foreground">{idx + 1}</td>
                  <td className="px-4 py-2 font-mono text-xs text-foreground/80">{step.stackStates.join(", ")}</td>
                  <td className="px-4 py-2 font-mono text-xs text-foreground/80">
                    {step.stackSymbols.join(", ") || "(empty)"}
                  </td>
                  <td className="px-4 py-2 font-mono text-xs text-foreground/80">{step.input}</td>
                  <td className="px-4 py-2">
                    <ActionBadge action={step.action} />
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

function ActionBadge({ action }: { action: any }) {
  const baseClass = "px-2 py-1 rounded text-xs font-semibold"

  if (action.type === "shift") {
    return <span className={`${baseClass} bg-blue-500/20 text-blue-600`}>shift {action.to}</span>
  }

  if (action.type === "reduce") {
    return <span className={`${baseClass} bg-orange-500/20 text-orange-600`}>reduce {action.production.text}</span>
  }

  if (action.type === "goto") {
    return <span className={`${baseClass} bg-purple-500/20 text-purple-600`}>goto {action.to}</span>
  }

  if (action.type === "accept") {
    return <span className={`${baseClass} bg-green-500/20 text-green-600`}>accept</span>
  }

  return <span className={`${baseClass} bg-red-500/20 text-red-600`}>error</span>
}
