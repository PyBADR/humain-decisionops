'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { fraudApi } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { Shield, AlertTriangle } from 'lucide-react'

export default function FraudScenariosPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [selectedScenario, setSelectedScenario] = useState<any>(null)

  const { data: scenarios, isLoading } = useQuery({
    queryKey: ['fraud-scenarios'],
    queryFn: fraudApi.listScenarios,
  })

  const { data: scenarioDetail } = useQuery({
    queryKey: ['fraud-scenario', selectedScenario?.id],
    queryFn: () => fraudApi.getScenario(selectedScenario.id),
    enabled: !!selectedScenario,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => fraudApi.updateScenario(id, data),
    onSuccess: () => {
      toast({ title: 'Scenario updated' })
      queryClient.invalidateQueries({ queryKey: ['fraud-scenarios'] })
    },
  })

  const handleThresholdChange = (id: string, value: number[]) => {
    updateMutation.mutate({ id, data: { threshold: value[0] } })
  }

  const handleEnabledChange = (id: string, enabled: boolean) => {
    updateMutation.mutate({ id, data: { enabled } })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Shield className="h-8 w-8 text-amber-400" />
          Fraud Scenario Library
        </h1>
        <p className="text-muted-foreground">Configure fraud detection scenarios and thresholds</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Scenarios</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="py-8 text-center text-muted-foreground">Loading...</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Scenario</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Threshold</TableHead>
                    <TableHead>Hits</TableHead>
                    <TableHead>Enabled</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {scenarios?.map((scenario: any) => (
                    <TableRow
                      key={scenario.id}
                      className="cursor-pointer"
                      onClick={() => setSelectedScenario(scenario)}
                    >
                      <TableCell>
                        <div>
                          <p className="font-medium">{scenario.name}</p>
                          <p className="text-sm text-muted-foreground truncate max-w-[300px]">
                            {scenario.description}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{scenario.category}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="w-32">
                          <Slider
                            value={[scenario.threshold]}
                            min={0}
                            max={1}
                            step={0.05}
                            onValueChange={(value) => handleThresholdChange(scenario.id, value)}
                            onClick={(e) => e.stopPropagation()}
                          />
                          <span className="text-xs text-muted-foreground">
                            {(scenario.threshold * 100).toFixed(0)}%
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={scenario.hits_count > 0 ? 'high-risk' : 'outline'}>
                          {scenario.hits_count}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={scenario.enabled}
                          onCheckedChange={(checked) => handleEnabledChange(scenario.id, checked)}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Scenario Details</CardTitle>
          </CardHeader>
          <CardContent>
            {selectedScenario ? (
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium">{selectedScenario.name}</h3>
                  <Badge variant="outline" className="mt-1">{selectedScenario.category}</Badge>
                </div>
                <p className="text-sm text-muted-foreground">{selectedScenario.description}</p>
                <div>
                  <h4 className="text-sm font-medium mb-2">Recent Hits</h4>
                  {scenarioDetail?.recent_hits?.length > 0 ? (
                    <div className="space-y-2">
                      {scenarioDetail.recent_hits.map((hit: any) => (
                        <div key={hit.id} className="p-2 bg-secondary rounded text-sm">
                          <div className="flex items-center justify-between">
                            <span className="font-mono">{hit.claim_id.slice(0, 8)}...</span>
                            <Badge variant="high-risk">{(hit.score * 100).toFixed(0)}%</Badge>
                          </div>
                          <p className="text-muted-foreground text-xs mt-1">{hit.explanation}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No recent hits</p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">Select a scenario to view details</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
