'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { fastLaneApi } from '@/lib/api'
import { formatCurrency, formatDateTime } from '@/lib/utils'
import { useToast } from '@/components/ui/use-toast'
import { Zap, AlertTriangle } from 'lucide-react'

export default function FastLanePage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [overrideDialog, setOverrideDialog] = useState<{ open: boolean; claimId: string | null }>({
    open: false,
    claimId: null,
  })
  const [overrideReason, setOverrideReason] = useState('')

  const { data: queue, isLoading } = useQuery({
    queryKey: ['fast-lane-queue'],
    queryFn: fastLaneApi.getQueue,
  })

  const overrideMutation = useMutation({
    mutationFn: ({ claimId, reason }: { claimId: string; reason: string }) =>
      fastLaneApi.override(claimId, reason),
    onSuccess: () => {
      toast({ title: 'Override successful', description: 'Claim moved to review queue' })
      queryClient.invalidateQueries({ queryKey: ['fast-lane-queue'] })
      setOverrideDialog({ open: false, claimId: null })
      setOverrideReason('')
    },
    onError: () => {
      toast({ title: 'Error', description: 'Failed to override claim', variant: 'destructive' })
    },
  })

  const handleOverride = () => {
    if (overrideDialog.claimId && overrideReason) {
      overrideMutation.mutate({ claimId: overrideDialog.claimId, reason: overrideReason })
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Zap className="h-8 w-8 text-blue-400" />
          Fast Lane Queue
        </h1>
        <p className="text-muted-foreground">Auto-approve eligible claims with human oversight</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Eligible Claims</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-8 text-center text-muted-foreground">Loading...</div>
          ) : queue && queue.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Claim ID</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Triage</TableHead>
                  <TableHead>Risk</TableHead>
                  <TableHead>Auto-Approve Ready</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {queue.map((claim: any) => (
                  <TableRow key={claim.id}>
                    <TableCell>
                      <Link href={`/claims/${claim.id}`} className="text-primary hover:underline font-mono text-sm">
                        {claim.claim_number}
                      </Link>
                    </TableCell>
                    <TableCell>{claim.customer_name}</TableCell>
                    <TableCell>{claim.claim_type}</TableCell>
                    <TableCell>{formatCurrency(claim.amount)}</TableCell>
                    <TableCell>
                      <Badge variant={claim.triage_label === 'STP' ? 'stp' : 'review'}>
                        {claim.triage_label}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className={`font-mono text-sm ${claim.risk_score > 0.3 ? 'text-amber-400' : 'text-green-400'}`}>
                        {(claim.risk_score * 100).toFixed(0)}%
                      </span>
                    </TableCell>
                    <TableCell>
                      {claim.auto_approve_ready ? (
                        <Badge variant="stp">Ready</Badge>
                      ) : (
                        <Badge variant="outline">Needs Review</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setOverrideDialog({ open: true, claimId: claim.id })}
                      >
                        <AlertTriangle className="h-4 w-4 mr-1" />
                        Override
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="py-8 text-center text-muted-foreground">
              No claims in fast lane queue
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={overrideDialog.open} onOpenChange={(open) => setOverrideDialog({ open, claimId: null })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Override Fast Lane Claim</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-muted-foreground mb-4">
              This will move the claim to the review queue and create an audit event.
            </p>
            <Textarea
              placeholder="Enter reason for override..."
              value={overrideReason}
              onChange={(e) => setOverrideReason(e.target.value)}
              rows={4}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOverrideDialog({ open: false, claimId: null })}>
              Cancel
            </Button>
            <Button onClick={handleOverride} disabled={!overrideReason || overrideMutation.isPending}>
              {overrideMutation.isPending ? 'Processing...' : 'Confirm Override'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
