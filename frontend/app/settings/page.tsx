'use client'

import { useEffect, useState } from 'react'
import { healthApi } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, CheckCircle2, Cpu, Database, Server, Zap } from 'lucide-react'

interface HealthStatus {
  status: string
  version: string
  database: boolean
  database_error?: string
  vector_store: boolean
  llm_provider: string
  mode: string
  heuristic_mode: boolean
}

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await healthApi.check()
        setHealth(data)
      } catch (err) {
        setError('Failed to connect to backend API')
      } finally {
        setLoading(false)
      }
    }
    fetchHealth()
  }, [])

  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'openai':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'ollama':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'heuristic':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
      default:
        return 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30'
    }
  }

  const getModeDescription = (mode: string) => {
    switch (mode) {
      case 'openai':
        return 'Using OpenAI GPT-4o-mini for intelligent extraction and rationale generation.'
      case 'ollama':
        return 'Using local Ollama LLM for extraction and rationale generation.'
      case 'heuristic':
        return 'Running in heuristic mode. Pipeline uses rule-based logic without LLM calls. All features work but extraction and rationale are template-based.'
      default:
        return 'Unknown mode'
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-100">Settings</h1>
        <p className="text-zinc-400 mt-1">System configuration and status</p>
      </div>

      {/* Mode Banner */}
      {health && (
        <div className={`rounded-lg border p-4 ${getModeColor(health.mode)}`}>
          <div className="flex items-start gap-3">
            {health.mode === 'heuristic' ? (
              <Zap className="h-5 w-5 mt-0.5" />
            ) : (
              <Cpu className="h-5 w-5 mt-0.5" />
            )}
            <div>
              <h3 className="font-medium">
                Operating Mode: <span className="uppercase">{health.mode}</span>
              </h3>
              <p className="text-sm mt-1 opacity-90">
                {getModeDescription(health.mode)}
              </p>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="text-zinc-400">Loading system status...</div>
      )}

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {health && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {/* System Status */}
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                <Server className="h-4 w-4" />
                System Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {health.status === 'healthy' ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
                <span className="text-xl font-semibold text-zinc-100 capitalize">
                  {health.status}
                </span>
              </div>
              <p className="text-sm text-zinc-500 mt-1">Version {health.version}</p>
            </CardContent>
          </Card>

          {/* Database Status */}
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                <Database className="h-4 w-4" />
                Database
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {health.database ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
                <span className="text-xl font-semibold text-zinc-100">
                  {health.database ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              {health.database_error && (
                <p className="text-sm text-red-400 mt-1">{health.database_error}</p>
              )}
            </CardContent>
          </Card>

          {/* LLM Provider */}
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                LLM Provider
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Badge className={getModeColor(health.llm_provider)}>
                {health.llm_provider.toUpperCase()}
              </Badge>
              <p className="text-sm text-zinc-500 mt-2">
                {health.heuristic_mode
                  ? 'No LLM - using rule-based heuristics'
                  : `Using ${health.llm_provider} for AI features`}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Configuration Info */}
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-zinc-100">Environment Configuration</CardTitle>
          <CardDescription>
            Configure these environment variables to change system behavior
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h4 className="font-medium text-zinc-300">Backend Variables</h4>
                <ul className="space-y-1 text-zinc-400">
                  <li><code className="text-amber-400">DATABASE_URL</code> - PostgreSQL connection string</li>
                  <li><code className="text-amber-400">HEURISTIC_MODE</code> - Force heuristic mode (true/false)</li>
                  <li><code className="text-amber-400">OPENAI_API_KEY</code> - Enable OpenAI LLM</li>
                  <li><code className="text-amber-400">OLLAMA_BASE_URL</code> - Local Ollama server URL</li>
                  <li><code className="text-amber-400">CORS_ALLOW_ORIGINS</code> - Allowed frontend origins</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-zinc-300">Frontend Variables</h4>
                <ul className="space-y-1 text-zinc-400">
                  <li><code className="text-amber-400">NEXT_PUBLIC_API_URL</code> - Backend API URL</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
