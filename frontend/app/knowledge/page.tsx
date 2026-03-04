'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { knowledgeApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import { useToast } from '@/components/ui/use-toast'
import { BookOpen, Upload, RefreshCw, Search } from 'lucide-react'

export default function KnowledgePage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [testQuery, setTestQuery] = useState('')
  const [testResults, setTestResults] = useState<any>(null)

  const { data: documents, isLoading } = useQuery({
    queryKey: ['knowledge-documents'],
    queryFn: knowledgeApi.listDocuments,
  })

  const { data: status } = useQuery({
    queryKey: ['knowledge-status'],
    queryFn: knowledgeApi.status,
  })

  const rebuildMutation = useMutation({
    mutationFn: knowledgeApi.rebuild,
    onSuccess: (data) => {
      toast({ title: 'Index rebuilt', description: `Processed ${data.total_chunks} chunks` })
      queryClient.invalidateQueries({ queryKey: ['knowledge-documents'] })
      queryClient.invalidateQueries({ queryKey: ['knowledge-status'] })
    },
    onError: () => {
      toast({ title: 'Error', description: 'Failed to rebuild index', variant: 'destructive' })
    },
  })

  const testMutation = useMutation({
    mutationFn: (query: string) => knowledgeApi.test(query),
    onSuccess: (data) => {
      setTestResults(data)
    },
  })

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('name', file.name.replace(/\.[^/.]+$/, ''))
    formData.append('file', file)

    try {
      await knowledgeApi.upload(formData)
      toast({ title: 'Document uploaded', description: 'Run rebuild to index the document' })
      queryClient.invalidateQueries({ queryKey: ['knowledge-documents'] })
    } catch {
      toast({ title: 'Error', description: 'Failed to upload document', variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BookOpen className="h-8 w-8 text-blue-400" />
            Knowledge Base
          </h1>
          <p className="text-muted-foreground">Manage policy documents and vector index</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <label>
              <Upload className="h-4 w-4 mr-2" />
              Upload Policy
              <input type="file" className="hidden" accept=".pdf" onChange={handleUpload} />
            </label>
          </Button>
          <Button onClick={() => rebuildMutation.mutate()} disabled={rebuildMutation.isPending}>
            <RefreshCw className={`h-4 w-4 mr-2 ${rebuildMutation.isPending ? 'animate-spin' : ''}`} />
            Rebuild Index
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Total Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.total_documents ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Indexed Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.indexed_documents ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Total Chunks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.total_chunks ?? 0}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Documents Table */}
        <Card>
          <CardHeader>
            <CardTitle>Policy Documents</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="py-8 text-center text-muted-foreground">Loading...</div>
            ) : documents && documents.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Chunks</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {documents.map((doc: any) => (
                    <TableRow key={doc.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{doc.name}</p>
                          <p className="text-sm text-muted-foreground">{doc.filename}</p>
                        </div>
                      </TableCell>
                      <TableCell>{doc.chunk_count}</TableCell>
                      <TableCell>
                        <Badge variant={doc.indexed ? 'stp' : 'review'}>
                          {doc.indexed ? 'Indexed' : 'Pending'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-muted-foreground">No documents uploaded</p>
            )}
          </CardContent>
        </Card>

        {/* Test Retrieval */}
        <Card>
          <CardHeader>
            <CardTitle>Test Retrieval</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter test query..."
                  value={testQuery}
                  onChange={(e) => setTestQuery(e.target.value)}
                />
                <Button
                  onClick={() => testMutation.mutate(testQuery)}
                  disabled={!testQuery || testMutation.isPending}
                >
                  <Search className="h-4 w-4" />
                </Button>
              </div>
              {testResults && (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    {testResults.results?.length ?? 0} results in {testResults.latency_ms}ms
                  </p>
                  {testResults.results?.map((result: any, i: number) => (
                    <div key={i} className="p-3 bg-secondary rounded">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{result.document_name}</span>
                        <Badge variant="outline">{(result.relevance_score * 100).toFixed(0)}%</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{result.content}</p>
                      {result.page_number && (
                        <p className="text-xs text-muted-foreground mt-1">Page {result.page_number}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
