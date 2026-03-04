'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { claimsApi, auditApi } from '@/lib/api'
import { formatCurrency, formatDateTime } from '@/lib/utils'
import { useToast } from '@/components/ui/use-toast'
import { Play, FileText, Code, BookOpen, Shield, CheckCircle, Clock, AlertTriangle } from 'lucide-react'

export default function ClaimDetailPage() {
  const params = useParams()
  const claimId = params.id as string
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('document')

  const { data, isLoading } = useQuery({
    queryKey: ['claim', claimId],
    queryFn: () => claimsApi.get(claimId),
  })

  const { data: auditEvents } = useQuery({
    queryKey: ['audit', claimId],
    queryFn: () => auditApi.list({ claim_id: claimId }),
  })

  const runPipeline = useMutation({
    mutationFn: () => claimsApi.runPipeline(claimId),
    onSuccess: () => {
      toast({ title: 'Pipeline started', description: 'Processing claim...' })
      queryClient.invalidateQueries({ queryKey: ['claim', claimId] })
    },
    onError: () => {
      toast({ title: 'Error', description: 'Failed to start pipeline', variant: 'destructive' })
    },
  })

  if (isLoading) {
    return <div className="flex items-center justify-center py-12">Loading...</div>
  }

  const claim = data?.claim
  const documents = data?.documents || []
  const extraction = data?.extraction
  const riskScore = data?.risk_score
  const decision = data?.decision
  const fraudHits = data?.fraud_hits || []
  const runs = data?.runs || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold font-mono">{claim?.claim_number}</h1>
            <Badge
              variant={
                claim?.triage_label === 'STP'
                  ? 'stp'
                  : claim?.triage_label === 'HIGH_RISK'
                  ? 'high-risk'
                  : 'review'
              }
            >
              {claim?.triage_label}
            </Badge>
            <Badge
              variant={
                claim?.decision_status === 'APPROVE'
                  ? 'approve'
                  : claim?.decision_status === 'REJECT'
                  ? 'reject'
                  : 'pending'
              }
            >
              {claim?.decision_status}
            </Badge>
          </div>
          <p className="text-muted-foreground mt-1">
            {claim?.customer_name} • {claim?.claim_type} • {formatCurrency(claim?.amount || 0)}
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => runPipeline.mutate()} disabled={runPipeline.isPending}>
            <Play className="h-4 w-4 mr-2" />
            {runPipeline.isPending ? 'Running...' : 'Run Pipeline'}
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="document"><FileText className="h-4 w-4 mr-2" />Document</TabsTrigger>
          <TabsTrigger value="extraction"><Code className="h-4 w-4 mr-2" />Extraction</TabsTrigger>
          <TabsTrigger value="policy"><BookOpen className="h-4 w-4 mr-2" />Policy Matches</TabsTrigger>
          <TabsTrigger value="risk"><Shield className="h-4 w-4 mr-2" />Risk/Fraud</TabsTrigger>
          <TabsTrigger value="decision"><CheckCircle className="h-4 w-4 mr-2" />Decision</TabsTrigger>
          <TabsTrigger value="audit"><Clock className="h-4 w-4 mr-2" />Audit Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="document" className="mt-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Documents</CardTitle></CardHeader>
              <CardContent>
                {documents.length > 0 ? (
                  <div className="space-y-4">
                    {documents.map((doc: any) => (
                      <div key={doc.id} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">{doc.filename}</p>
                            <p className="text-sm text-muted-foreground">
                              {doc.file_type} • {(doc.file_size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                          <Badge
                            variant={
                              doc.forensics_risk === 'HIGH'
                                ? 'high-risk'
                                : doc.forensics_risk === 'MED'
                                ? 'review'
                                : 'stp'
                            }
                          >
                            {doc.forensics_risk} Risk
                          </Badge>
                        </div>
                        {doc.forensics_signals?.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {doc.forensics_signals.map((signal: any) => (
                              <div key={signal.id} className="flex items-start gap-2 text-sm">
                                <AlertTriangle className={`h-4 w-4 mt-0.5 ${signal.severity === 'HIGH' ? 'text-red-400' : 'text-amber-400'}`} />
                                <div>
                                  <p className="font-medium">{signal.signal_type}</p>
                                  <p className="text-muted-foreground">{signal.description}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No documents uploaded</p>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Claim Details</CardTitle></CardHeader>
              <CardContent>
                <dl className="space-y-3">
                  <div><dt className="text-sm text-muted-foreground">Policy Number</dt><dd className="font-mono">{claim?.policy_number}</dd></div>
                  <div><dt className="text-sm text-muted-foreground">Incident Date</dt><dd>{claim?.incident_date}</dd></div>
                  <div><dt className="text-sm text-muted-foreground">Location</dt><dd>{claim?.incident_location || 'N/A'}</dd></div>
                  <div><dt className="text-sm text-muted-foreground">Description</dt><dd className="text-sm">{claim?.description || 'N/A'}</dd></div>
                </dl>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="extraction" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Extracted Fields</CardTitle>
                {extraction && (
                  <Badge variant={extraction.schema_valid ? 'stp' : 'high-risk'}>
                    {extraction.schema_valid ? 'Valid Schema' : 'Validation Errors'}
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {extraction ? (
                <pre className="bg-secondary p-4 rounded-lg overflow-auto text-sm">
                  {JSON.stringify(extraction.extracted_data, null, 2)}
                </pre>
              ) : (
                <p className="text-muted-foreground">No extraction data. Run the pipeline to extract fields.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="policy" className="mt-6">
          <Card>
            <CardHeader><CardTitle>Policy Matches</CardTitle></CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Policy context retrieved during pipeline execution will appear here.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risk" className="mt-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Risk Assessment</CardTitle></CardHeader>
              <CardContent>
                {riskScore ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-4">
                      <div className="text-4xl font-bold">{(riskScore.overall_score * 100).toFixed(0)}%</div>
                      <div className="flex-1 h-4 bg-secondary rounded-full overflow-hidden">
                        <div className={`h-full ${riskScore.overall_score > 0.7 ? 'bg-red-500' : riskScore.overall_score > 0.4 ? 'bg-amber-500' : 'bg-green-500'}`} style={{ width: `${riskScore.overall_score * 100}%` }} />
                      </div>
                    </div>
                    <div className="space-y-2">
                      {riskScore.factors?.map((factor: any, i: number) => (
                        <div key={i} className="flex items-center justify-between text-sm">
                          <span>{factor.name}</span>
                          <span className="text-muted-foreground">{(factor.score * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">No risk assessment. Run the pipeline.</p>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Fraud Hits</CardTitle></CardHeader>
              <CardContent>
                {fraudHits.length > 0 ? (
                  <div className="space-y-3">
                    {fraudHits.map((hit: any) => (
                      <div key={hit.id} className="p-3 border rounded-lg">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{hit.scenario_name || 'Fraud Scenario'}</span>
                          <Badge variant="high-risk">{(hit.score * 100).toFixed(0)}%</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{hit.explanation}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No fraud hits detected</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="decision" className="mt-6">
          <Card>
            <CardHeader><CardTitle>Decision</CardTitle></CardHeader>
            <CardContent>
              {decision ? (
                <div className="space-y-6">
                  <div className="flex items-center gap-4">
                    <Badge variant={decision.status === 'APPROVE' ? 'approve' : decision.status === 'REJECT' ? 'reject' : 'review'} className="text-lg px-4 py-2">
                      {decision.status}
                    </Badge>
                    <div>
                      <p className="text-sm text-muted-foreground">Confidence</p>
                      <p className="text-2xl font-bold">{(decision.confidence * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Rationale</h4>
                    <p className="text-muted-foreground">{decision.rationale}</p>
                  </div>
                  {decision.next_actions?.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Next Actions</h4>
                      <ul className="list-disc list-inside text-muted-foreground">
                        {decision.next_actions.map((action: string, i: number) => (
                          <li key={i}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground">No decision yet. Run the pipeline.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="mt-6">
          <Card>
            <CardHeader><CardTitle>Audit Timeline</CardTitle></CardHeader>
            <CardContent>
              {auditEvents && auditEvents.length > 0 ? (
                <div className="space-y-4">
                  {auditEvents.map((event: any) => (
                    <div key={event.id} className="flex gap-4 pb-4 border-b last:border-0">
                      <div className="w-2 h-2 mt-2 rounded-full bg-primary" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{event.event_type}</span>
                          <span className="text-sm text-muted-foreground">{formatDateTime(event.created_at)}</span>
                        </div>
                        <p className="text-sm text-muted-foreground">Actor: {event.actor}</p>
                        {Object.keys(event.payload || {}).length > 0 && (
                          <pre className="mt-2 text-xs bg-secondary p-2 rounded overflow-auto">
                            {JSON.stringify(event.payload, null, 2)}
                          </pre>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No audit events</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
