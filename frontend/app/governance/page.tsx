'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { auditApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import { FileCheck, Download, Search } from 'lucide-react'

export default function GovernancePage() {
  const [eventTypeFilter, setEventTypeFilter] = useState('')

  const { data: events, isLoading } = useQuery({
    queryKey: ['audit-events', eventTypeFilter],
    queryFn: () => {
      const params: Record<string, string> = {}
      if (eventTypeFilter) params.event_type = eventTypeFilter
      return auditApi.list(params)
    },
  })

  const eventTypes = [
    'claim_created',
    'document_uploaded',
    'pipeline_started',
    'triage_assigned',
    'decision_made',
    'fraud_alert',
    'fast_lane_override',
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <FileCheck className="h-8 w-8 text-purple-400" />
            Governance & Audit
          </h1>
          <p className="text-muted-foreground">Complete audit trail of all system events</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <a href={auditApi.exportCsv()} download>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </a>
          </Button>
          <Button variant="outline" asChild>
            <a href={auditApi.exportJson()} download>
              <Download className="h-4 w-4 mr-2" />
              Export JSON
            </a>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <select
              value={eventTypeFilter}
              onChange={(e) => setEventTypeFilter(e.target.value)}
              className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">All Event Types</option>
              {eventTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Events Table */}
      <Card>
        <CardHeader>
          <CardTitle>Audit Events</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-8 text-center text-muted-foreground">Loading...</div>
          ) : events && events.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Event Type</TableHead>
                  <TableHead>Actor</TableHead>
                  <TableHead>Claim ID</TableHead>
                  <TableHead>Payload</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {events.map((event: any) => (
                  <TableRow key={event.id}>
                    <TableCell className="text-sm">
                      {formatDateTime(event.created_at)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{event.event_type}</Badge>
                    </TableCell>
                    <TableCell className="text-sm">{event.actor}</TableCell>
                    <TableCell className="font-mono text-sm">
                      {event.claim_id ? event.claim_id.slice(0, 8) + '...' : '-'}
                    </TableCell>
                    <TableCell>
                      <pre className="text-xs bg-secondary p-2 rounded max-w-md overflow-auto">
                        {JSON.stringify(event.payload, null, 2)}
                      </pre>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="py-8 text-center text-muted-foreground">
              No audit events found
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
