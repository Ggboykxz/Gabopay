/** Shared types and constants for GABOPAY */

export * from './tokens'
export * from './utils/currency'
export * from './components/TransactionBadge'

export const PAYMENT_METHODS = {
  AIRTEL_MONEY: 'airtel_money',
  MOOV_MONEY: 'moov_money',
  CARD: 'card',
  CASH: 'cash',
} as const

export const TRANSACTION_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  SUCCEEDED: 'succeeded',
  FAILED: 'failed',
  REFUNDED: 'refunded',
} as const

export const CURRENCY = {
  XAF: 'XAF',
} as const

export const API_KEY_PREFIX = {
  TEST: 'gp_test',
  LIVE: 'gp_live',
} as const

export const WEBHOOK_EVENTS = [
  'charge.succeeded',
  'charge.failed',
  'charge.pending',
  'refund.succeeded',
  'refund.failed',
  'payout.succeeded',
  'payout.failed',
] as const

export type PaymentMethod = typeof PAYMENT_METHODS[keyof typeof PAYMENT_METHODS]
export type TransactionStatus = typeof TRANSACTION_STATUS[keyof typeof TRANSACTION_STATUS]
export type WebhookEventType = typeof WEBHOOK_EVENTS[number]

export interface ApiError {
  code: string
  message: string
  type: string
  doc_url?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  has_more: boolean
  total: number
}