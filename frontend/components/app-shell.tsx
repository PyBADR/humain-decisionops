'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Inbox,
  Zap,
  Shield,
  BookOpen,
  Play,
  FileCheck,
  BarChart3,
  User,
  Settings,
  MessageSquare,
  Menu,
  X,
  Wifi,
  WifiOff,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { GlobalSearch } from '@/components/global-search'
import { useGlobalUpdates } from '@/hooks/use-websocket'

const navigation = [
  { name: 'Overview', href: '/overview', icon: LayoutDashboard },
  { name: 'Claims Inbox', href: '/claims', icon: Inbox },
  { name: 'Fast Lane', href: '/fast-lane', icon: Zap },
  { name: 'Fraud Scenarios', href: '/fraud-scenarios', icon: Shield },
  { name: 'Knowledge Base', href: '/knowledge', icon: BookOpen },
  { name: 'Agent Runs', href: '/runs', icon: Play },
  { name: 'Governance/Audit', href: '/governance', icon: FileCheck },
  { name: 'Metrics', href: '/metrics', icon: BarChart3 },
  { name: 'Intake', href: '/intake', icon: MessageSquare },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { isConnected, newClaims } = useGlobalUpdates()

  return (
    <div className="min-h-screen bg-background">
      {/* Top bar */}
      <header className="fixed top-0 left-0 right-0 z-50 h-14 border-b border-border bg-card">
        <div className="flex h-full items-center justify-between px-4">
          {/* Left */}
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <Link href="/overview" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">H</span>
              </div>
              <span className="font-semibold text-lg hidden sm:block">Humain DecisionOps</span>
            </Link>
          </div>

          {/* Center - Global Search */}
          <div className="flex-1 max-w-xl mx-4">
            <GlobalSearch />
          </div>

          {/* Right */}
          <div className="flex items-center gap-2">
            {/* WebSocket Status Indicator */}
            <div className="flex items-center gap-1 px-2 py-1 rounded bg-secondary" title={isConnected ? 'Real-time updates active' : 'Real-time updates disconnected'}>
              {isConnected ? (
                <Wifi className="h-3 w-3 text-green-500" />
              ) : (
                <WifiOff className="h-3 w-3 text-zinc-500" />
              )}
              <span className="text-xs text-muted-foreground">LIVE</span>
            </div>
            {newClaims.length > 0 && (
              <span className="px-2 py-1 text-xs rounded bg-blue-500/20 text-blue-400">
                {newClaims.length} new
              </span>
            )}
            <span className="px-2 py-1 text-xs rounded bg-secondary text-muted-foreground">
              DEV
            </span>
            <Button variant="ghost" size="icon" asChild>
              <Link href="/settings">
                <Settings className="h-5 w-5" />
              </Link>
            </Button>
            <Button variant="ghost" size="icon">
              <User className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-14 bottom-0 z-40 w-64 border-r border-border bg-card transition-transform duration-200',
          !sidebarOpen && '-translate-x-full'
        )}
      >
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main
        className={cn(
          'pt-14 transition-all duration-200',
          sidebarOpen ? 'pl-64' : 'pl-0'
        )}
      >
        <div className="p-6">{children}</div>
      </main>
    </div>
  )
}
