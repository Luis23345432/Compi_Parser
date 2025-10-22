import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface DerivationTreeProps {
  tree: any
  treeAscii: string
}

export default function DerivationTree({ tree, treeAscii }: DerivationTreeProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Derivation Tree</CardTitle>
        <CardDescription>Parse tree showing the derivation of the input</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="ascii" className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="ascii">ASCII View</TabsTrigger>
            <TabsTrigger value="visual">Visual Tree</TabsTrigger>
          </TabsList>

          <TabsContent value="ascii" className="mt-4">
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono text-foreground/80">
              {treeAscii}
            </pre>
          </TabsContent>

          <TabsContent value="visual" className="mt-4">
            <div className="flex justify-center p-8 bg-muted rounded-lg overflow-x-auto">
              <TreeNode node={tree} />
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

function TreeNode({ node }: { node: any }) {
  const isLeaf = !node.children || node.children.length === 0

  return (
    <div className="flex flex-col items-center">
      <div className="px-3 py-1 bg-primary text-primary-foreground rounded font-mono text-sm font-bold">
        {node.label}
      </div>
      {!isLeaf && (
        <div className="flex gap-8 mt-4">
          {node.children.map((child: any, idx: number) => (
            <div key={idx} className="flex flex-col items-center">
              <div className="w-0.5 h-4 bg-border"></div>
              <TreeNode node={child} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
