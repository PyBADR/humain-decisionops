'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { claimsApi } from '@/lib/api'
import { formatCurrency, formatDateTime } from '@/lib/utils'
import { Search, Filter, RefreshCw } from 'lucide-react'

export default function ClaimsPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [triageFilter, setTriageFilter] = useState('')

  const { data: claims, isLoading, refetch } = useQuery({
    queryKey: ['claims', search, statusFilter, triageFilter],
    queryFn: () => {
      const params: Record<string, string> = {}
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      if (triageFilter) params.triage = triageFilter
      return claimsApi.list(params)
    },
  })

  const triageOptions = ['STP', 'REVIEW', 'HIGH_RISK']
  const statusOptions = ['PENDING', 'APPROVE', 'REVIEW', 'REJECT']

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Claims Inbox</h1>
          <p className="text-muted-foreground">Manage and process insurance claims</p>
        </div>
        <Button onClick={() => refetch()} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search claims..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <select
                value={triageFilter}
                onChange={(e) => setTriageFilter(e.target.value)}
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="">All Triage</option>
                {triageOptions.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="">All Status</option>
                {statusOptions.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Claims Table */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Claim ID</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Triage</TableHead>
                  <TableHead>Fraud Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Fast Lane</TableHead>
                  <TableHead>Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {claims?.map((claim: any) => (
                  <TableRow key={claim.id} className="cursor-pointer hover:bg-muted/50">
                    <TableCell>
                      <Link
                        href={`/claims/${claim.id}`}
                        className="text-primary hover:underline font-mono text-sm"
                      >
                        {claim.claim_number}
                      </Link>
                    </TableCell>
                    <TableCell>{claim.customer_name}</TableCell>
                    <TableCell className="text-sm">{claim.claim_type}</TableCell>
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
                      <span
                        className={`font-mono text-sm ${
                          claim.fraud_score > 0.7
                            ? 'text-red-400'
                            : claim.fraud_score > 0.4
                            ? 'text-amber-400'
                            : 'text-green-400'
                        }`}
                      >
                        {(claim.fraud_score * 100).toFixed(0)}%
                      </span>
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
                    <TableCell>
                      {claim.fast_lane_eligible && (
                        <Badge variant="outline" className="text-blue-400 border-blue-400/30">
                          Eligible
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {formatDateTime(claim.updated_at)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {claims?.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No claims found matching your filters
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
