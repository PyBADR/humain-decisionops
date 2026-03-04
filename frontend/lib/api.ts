const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}

// Claims API
export const claimsApi = {
  list: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : ''
    return fetchApi<any[]>(`/api/claims${query}`)
  },
  get: (id: string) => fetchApi<any>(`/api/claims/${id}`),
  create: (data: FormData) =>
    fetch(`${API_URL}/api/claims`, {
      method: 'POST',
      body: data,
    }).then((r) => r.json()),
  runPipeline: (id: string) =>
    fetchApi<any>(`/api/claims/${id}/run`, { method: 'POST' }),
}

// Runs API
export const runsApi = {
  list: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : ''
    return fetchApi<any[]>(`/api/runs${query}`)
  },
  get: (id: string) => fetchApi<any>(`/api/runs/${id}`),
}

// Audit API
export const auditApi = {
  list: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : ''
    return fetchApi<any[]>(`/api/audit${query}`)
  },
  exportJson: (claimId?: string) => {
    const query = claimId ? `?claim_id=${claimId}` : ''
    return `${API_URL}/api/audit/export/json${query}`
  },
  exportCsv: (claimId?: string) => {
    const query = claimId ? `?claim_id=${claimId}` : ''
    return `${API_URL}/api/audit/export/csv${query}`
  },
}

// Knowledge API
export const knowledgeApi = {
  listDocuments: () => fetchApi<any[]>('/api/knowledge/documents'),
  upload: (data: FormData) =>
    fetch(`${API_URL}/api/knowledge/upload`, {
      method: 'POST',
      body: data,
    }).then((r) => r.json()),
  rebuild: () => fetchApi<any>('/api/knowledge/rebuild', { method: 'POST' }),
  test: (query: string, topK: number = 5) => {
    const formData = new FormData()
    formData.append('query', query)
    formData.append('top_k', topK.toString())
    return fetch(`${API_URL}/api/knowledge/test`, {
      method: 'POST',
      body: formData,
    }).then((r) => r.json())
  },
  status: () => fetchApi<any>('/api/knowledge/status'),
}

// Fraud API
export const fraudApi = {
  listScenarios: () => fetchApi<any[]>('/api/fraud/scenarios'),
  getScenario: (id: string) => fetchApi<any>(`/api/fraud/scenarios/${id}`),
  updateScenario: (id: string, data: { threshold?: number; enabled?: boolean }) =>
    fetchApi<any>(`/api/fraud/scenarios/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  listHits: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : ''
    return fetchApi<any[]>(`/api/fraud/hits${query}`)
  },
}

// Fast Lane API
export const fastLaneApi = {
  getQueue: () => fetchApi<any[]>('/api/fast-lane/queue'),
  override: (claimId: string, reason: string) =>
    fetchApi<any>(`/api/fast-lane/${claimId}/override?reason=${encodeURIComponent(reason)}`, {
      method: 'POST',
    }),
  listOverrides: () => fetchApi<any[]>('/api/fast-lane/overrides'),
}

// Intake API
export const intakeApi = {
  submit: (data: any) =>
    fetchApi<any>('/api/intake/submit', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  listTranscripts: () => fetchApi<any[]>('/api/intake/transcripts'),
  getTranscript: (id: string) => fetchApi<any>(`/api/intake/transcripts/${id}`),
}

// Health & Metrics API
export const healthApi = {
  check: () => fetchApi<any>('/health'),
  metrics: () => fetchApi<any>('/metrics'),
}
