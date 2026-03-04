'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { healthApi, claimsApi } from '@/lib/api'
import { formatCurrency, formatDateTime } from '@/lib/utils'
import { TrendingUp, TrendingDown, Clock, Shield, FileCheck, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

export default function OverviewPage() {
  const { data: metrics } = useQuery({
    queryKey: ['metrics'],
    queryFn: healthApi.metrics,
    refetchInterval: 30000,
  })

  const { data: claims } = useQuery({
    queryKey: ['claims', 'recent'],
    queryFn: () => claimsApi.list({ page_size: '10' }),
    refetchInterval: 10000,
  })

  const kpis = [
    {
      title: 'Claims Today',
      value: metrics?.claims_today ?? 0,
      icon: FileCheck,
      trend: '+12%',
      trendUp: true,
    },
    {
      title: 'STP Rate',
      value: `${metrics?.stp_rate ?? 0}%`,
      icon: TrendingUp,
      trend: '+5%',
      trendUp: true,
    },
    {
      title: 'Fraud Hit Rate',
      value: `${metrics?.fraud_hit_rate ?? 0}%`,
      icon: Shield,
      trend: '-2%',
      trendUp: false,
    },
    {
      title: 'Avg Decision Time',
      value: `${((metrics?.avg_decision_time_ms ?? 0) / 1000).toFixed(1)}s`,
      icon: Clock,
      trend: '-15%',
      trendUp: true,
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Overview</h1>
        <p className="text-muted-foreground">Real-time claims processing dashboard</p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi) => (
          <Card key={kpi.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {kpi.title}
              </CardTitle>
              <kpi.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpi.value}</div>
              <p className={`text-xs ${kpi.trendUp ? 'text-green-500' : 'text-red-500'}`}>
                {kpi.trend} from last week
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Live Claims Stream */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Live Claims Stream</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Claim ID</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Triage</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {claims?.slice(0, 8).map((claim: any) => (
                  <TableRow key={claim.id}>
                    <TableCell>
                      <Link
                        href={`/claims/${claim.id}`}
                        className="text-primary hover:underline font-mono text-sm"
                      >
                        {claim.claim_number}
                      </Link>
                    </TableCell>
                    <TableCell>{claim.customer_name}</TableCell>
                    <TableCell>{formatCurrency(claim.amount)}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          claim.triage_label === 'STP'
                            ? 'stp'
                            : claim.triage_label === 'HIGH_RISK'
                            ? 'high-risk'
                            : 'review'
                        }
                      >
                        {claim.triage_label}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          claim.decision_status === 'APPROVE'
                            ? 'approve'
                            : claim.decision_status === 'REJECT'
                            ? 'reject'
                            : 'pending'
                        }
                      >
                        {claim.decision_status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {formatDateTime(claim.updated_at)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Decision Mix & Top Fraud */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Decision Mix</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-green-500" />
                    <span>Approved</span>
                  </div>
                  <span className="font-bold">{metrics?.decision_mix?.approve ?? 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-amber-500" />
                    <span>Review</span>
                  </div>
                  <span className="font-bold">{metrics?.decision_mix?.review ?? 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-red-500" />
                    <span>Rejected</span>
                  </div>
                  <span className="font-bold">{metrics?.decision_mix?.reject ?? 0}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" />
                Top Fraud Scenarios
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {metrics?.top_fraud_scenarios?.slice(0, 5).map((scenario: any, i: number) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm truncate max-w-[180px]">{scenario.name}</span>
                    <Badge variant="outline">{scenario.count}</Badge>
                  </div>
                ))}
                {(!metrics?.top_fraud_scenarios || metrics.top_fraud_scenarios.length === 0) && (
                  <p className="text-sm text-muted-foreground">No fraud scenarios triggered</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
