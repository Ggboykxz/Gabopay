/**
 * GABOPAY SDK Types
 */

export interface GabopayOptions {
  /** API Secret Key */
  secretKey: string
  /** Base URL for the API (optional, defaults to production) */
  baseUrl?: string
  /** Request timeout in milliseconds (default: 60000) */
  timeout?: number
  /** Maximum retry attempts (default: 3) */
  maxRetries?: number
}

export interface ChargeCreateOptions {
  /** Amount in XAF (lowest unit, e.g., 5000 = 5000 XAF) */
  amount: number
  /** Currency code (default: XAF) */
  currency?: string
  /** Payment method */
  method: 'airtel_money' | 'moov_money' | 'card'
  /** Phone number for mobile money */
  phone?: string
  /** Payment description */
  description?: string
  /** Custom metadata */
  metadata?: Record<string, unknown>
}

export interface Charge {
  id: string
  object: 'charge'
  amount: number
  currency: string
  status: 'pending' | 'processing' | 'succeeded' | 'failed' | 'refunded'
  method: string
  phone?: string
  description?: string
  metadata?: Record<string, unknown>
  fee_amount: number
  created: number
}

export interface RefundCreateOptions {
  /** Amount to refund in XAF */
  amount: number
  /** Reason for refund */
  reason?: string
}

export interface Refund {
  id: string
  object: 'refund'
  amount: number
  status: 'pending' | 'processing' | 'succeeded' | 'failed'
  reason?: string
  transaction_id: string
  created: number
}

export interface PayoutCreateOptions {
  /** Amount to withdraw in XAF */
  amount: number
  /** Payout method */
  method: 'airtel_money' | 'moov_money'
  /** Phone number for payout */
  phone: string
}

export interface Payout {
  id: string
  object: 'payout'
  amount: number
  method: string
  phone: string
  status: 'pending' | 'processing' | 'succeeded' | 'failed'
  created: number
}

export interface Balance {
  available: number
  pending: number
  currency: string
  updated_at: number
}

export interface WebhookEvent {
  id: string
  object: 'event'
  type: string
  data: {
    id: string
    amount: number
    currency: string
    status: string
    method: string
    metadata?: Record<string, unknown>
  }
  created: number
}