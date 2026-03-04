import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date))
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}m`
}

export function getTriageBadgeClass(triage: string): string {
  switch (triage) {
    case 'STP':
      return 'badge-stp'
    case 'REVIEW':
      return 'badge-review'
    case 'HIGH_RISK':
      return 'badge-high-risk'
    default:
      return 'badge-review'
  }
}

export function getDecisionBadgeClass(status: string): string {
  switch (status) {
    case 'APPROVE':
      return 'badge-approve'
    case 'REJECT':
      return 'badge-reject'
    case 'REVIEW':
      return 'badge-review'
    default:
      return 'badge-pending'
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'COMPLETED':
      return 'text-green-400'
    case 'RUNNING':
      return 'text-blue-400'
    case 'FAILED':
      return 'text-red-400'
    default:
      return 'text-gray-400'
  }
}
