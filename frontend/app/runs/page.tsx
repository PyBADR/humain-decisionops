'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { runsApi } from '@/lib/api'
import { formatDateTime, formatDuration, getStatusColor } from '@/lib/utils'
import { Play, ExternalLink } from 'lucide-react'

export default function RunsPage() {
  const { data: runs, isLoading } = useQuery({
    queryKey: ['runs'],
    queryFn: () => runsApi.list(),
    refetchInterval: 5000,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Play className="h-8 w-8 text-green-400" />
          Agent Runs
        </h1>
        <p className="text-muted-foreground">Monitor pipeline execution and traces</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Pipeline Runs</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-8 text-center text-muted-foreground">Loading...</div>
          ) : runs && runs.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Run ID</TableHead>
                  <TableHead>Claim</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Current Node</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Started</TableHead>
                  <TableHead>Trace</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runs.map((run: any) => (
                  <TableRow key={run.id}>
                    <TableCell className="font-mono text-sm">
                      {run.id.slice(0, 8)}...
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/claims/${run.claim_id}`}
                        className="text-primary hover:underline font-mono text-sm"
                      >
                        {run.claim_id.slice(0, 8)}...
                      </Link>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          run.status === 'COMPLETED'
                            ? 'stp'
                            : run.status === 'FAILED'
                            ? 'high-risk'
                            : run.status === 'RUNNING'
                            ? 'review'
                            : 'outline'
                        }
                      >
                        {run.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm">
                      {run.current_node || '-'}
                    </TableCell>
                    <TableCell className="text-sm">
                      {run.duration_ms ? formatDuration(run.duration_ms) : '-'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{run.provider}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDateTime(run.started_at)}
                    </TableCell>
                    <TableCell>
                      {run.trace_id ? (
                        <a
                          href={`https://smith.langchain.com/public/${run.trace_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline flex items-center gap-1"
                        >
                          View <ExternalLink className="h-3 w-3" />
                        </a>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="py-8 text-center text-muted-foreground">
              No pipeline runs yet
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
