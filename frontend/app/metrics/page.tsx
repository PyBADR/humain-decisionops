'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { healthApi } from '@/lib/api'
import { BarChart3, TrendingUp, Clock, Shield, CheckCircle, XCircle } from 'lucide-react'

export default function MetricsPage() {
  const { data: metrics } = useQuery({
    queryKey: ['metrics'],
    queryFn: healthApi.metrics,
    refetchInterval: 30000,
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.check,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <BarChart3 className="h-8 w-8 text-cyan-400" />
          Metrics Dashboard
        </h1>
        <p className="text-muted-foreground">System performance and health metrics</p>
      </div>

      {/* Health Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="flex items-center gap-3">
              {health?.status === 'healthy' ? (
                <CheckCircle className="h-6 w-6 text-green-400" />
              ) : (
                <XCircle className="h-6 w-6 text-red-400" />
              )}
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="font-medium capitalize">{health?.status || 'Unknown'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {health?.database ? (
                <CheckCircle className="h-6 w-6 text-green-400" />
              ) : (
                <XCircle className="h-6 w-6 text-red-400" />
              )}
              <div>
                <p className="text-sm text-muted-foreground">Database</p>
                <p className="font-medium">{health?.database ? 'Connected' : 'Disconnected'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {health?.vector_store ? (
                <CheckCircle className="h-6 w-6 text-green-400" />
              ) : (
                <XCircle className="h-6 w-6 text-red-400" />
              )}
              <div>
                <p className="text-sm text-muted-foreground">Vector Store</p>
                <p className="font-medium">{health?.vector_store ? 'Ready' : 'Not Ready'}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">LLM Provider</p>
              <p className="font-medium capitalize">{health?.llm_provider || 'Unknown'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Claims Today</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{metrics?.claims_today ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">STP Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{metrics?.stp_rate ?? 0}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Fraud Hit Rate</CardTitle>
            <Shield className="h-4 w-4 text-amber-400" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{metrics?.fraud_hit_rate ?? 0}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Decision Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {((metrics?.avg_decision_time_ms ?? 0) / 1000).toFixed(1)}s
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Decision Mix */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Decision Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm">Approved</span>
                  <span className="font-bold text-green-400">{metrics?.decision_mix?.approve ?? 0}</span>
                </div>
                <div className="h-3 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500"
                    style={{
                      width: `${((metrics?.decision_mix?.approve ?? 0) / ((metrics?.decision_mix?.approve ?? 0) + (metrics?.decision_mix?.review ?? 0) + (metrics?.decision_mix?.reject ?? 0) || 1)) * 100}%`,
                    }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm">Review</span>
                  <span className="font-bold text-amber-400">{metrics?.decision_mix?.review ?? 0}</span>
                </div>
                <div className="h-3 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-500"
                    style={{
                      width: `${((metrics?.decision_mix?.review ?? 0) / ((metrics?.decision_mix?.approve ?? 0) + (metrics?.decision_mix?.review ?? 0) + (metrics?.decision_mix?.reject ?? 0) || 1)) * 100}%`,
                    }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm">Rejected</span>
                  <span className="font-bold text-red-400">{metrics?.decision_mix?.reject ?? 0}</span>
                </div>
                <div className="h-3 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500"
                    style={{
                      width: `${((metrics?.decision_mix?.reject ?? 0) / ((metrics?.decision_mix?.approve ?? 0) + (metrics?.decision_mix?.review ?? 0) + (metrics?.decision_mix?.reject ?? 0) || 1)) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Fraud Scenarios</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {metrics?.top_fraud_scenarios?.map((scenario: any, i: number) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm truncate max-w-[250px]">{scenario.name}</span>
                  <span className="font-bold">{scenario.count}</span>
                </div>
              ))}
              {(!metrics?.top_fraud_scenarios || metrics.top_fraud_scenarios.length === 0) && (
                <p className="text-muted-foreground">No fraud scenarios triggered</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
