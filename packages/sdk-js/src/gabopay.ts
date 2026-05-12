/**
 * GABOPAY SDK Main Class
 */

import type {
  GabopayOptions,
  ChargeCreateOptions,
  Charge,
  RefundCreateOptions,
  Refund,
  PayoutCreateOptions,
  Payout,
  Balance,
} from './types'
import { GabopayError } from './errors'
import { Webhooks } from './webhooks'

const DEFAULT_BASE_URL = 'https://api.gabopay.ga'
const DEFAULT_TIMEOUT = 60000
const DEFAULT_MAX_RETRIES = 3

export class Gabopay {
  private secretKey: string
  private baseUrl: string
  private timeout: number
  private maxRetries: number

  public charges: Charges
  public refunds: Refunds
  public payouts: Payouts
  public balance: BalanceClient
  public webhooks: Webhooks

  constructor(options: GabopayOptions) {
    if (!options.secretKey) {
      throw new GabopayError('secretKey is required')
    }

    this.secretKey = options.secretKey
    this.baseUrl = options.baseUrl || DEFAULT_BASE_URL
    this.timeout = options.timeout || DEFAULT_TIMEOUT
    this.maxRetries = options.maxRetries || DEFAULT_MAX_RETRIES

    this.charges = new Charges(this)
    this.refunds = new Refunds(this)
    this.payouts = new Payouts(this)
    this.balance = new BalanceClient(this)
    this.webhooks = new Webhooks()
  }

  async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    let lastError: Error | null = null

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const response = await this.makeRequest<T>(method, path, body)
        return response
      } catch (error) {
        lastError = error as Error
        if (error instanceof GabopayError && error.statusCode && error.statusCode < 500) {
          throw error
        }
        if (attempt < this.maxRetries - 1) {
          await this.sleep(Math.pow(2, attempt) * 1000)
        }
      }
    }

    throw lastError
  }

  private async makeRequest<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-API-Key': this.secretKey,
    }

    const options: RequestInit = {
      method,
      headers,
      signal: AbortSignal.timeout(this.timeout),
    }

    if (body && ['POST', 'PATCH', 'PUT'].includes(method)) {
      options.body = JSON.stringify(body)
    }

    const response = await fetch(url, options)

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new GabopayError(
        error.error?.message || `Request failed with status ${response.status}`,
        response.status,
        error.error?.code
      )
    }

    return response.json()
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

class Charges {
  private client: Gabopay

  constructor(client: Gabopay) {
    this.client = client
  }

  async create(options: ChargeCreateOptions): Promise<Charge> {
    return this.client.request<Charge>('POST', '/v1/charges', options)
  }

  async get(chargeId: string): Promise<Charge> {
    return this.client.request<Charge>('GET', `/v1/charges/${chargeId}`)
  }

  async list(params?: {
    limit?: number
    status?: string
  }): Promise<{ data: Charge[]; has_more: boolean }> {
    const query = new URLSearchParams()
    if (params?.limit) query.set('limit', String(params.limit))
    if (params?.status) query.set('status', params.status)

    const path = `/v1/charges${query.toString() ? `?${query}` : ''}`
    return this.client.request('GET', path)
  }
}

class Refunds {
  private client: Gabopay

  constructor(client: Gabopay) {
    this.client = client
  }

  async create(transactionId: string, options: RefundCreateOptions): Promise<Refund> {
    return this.client.request<Refund>('POST', `/v1/refunds/${transactionId}`, options)
  }

  async get(refundId: string): Promise<Refund> {
    return this.client.request<Refund>('GET', `/v1/refunds/${refundId}`)
  }
}

class Payouts {
  private client: Gabopay

  constructor(client: Gabopay) {
    this.client = client
  }

  async create(options: PayoutCreateOptions): Promise<Payout> {
    return this.client.request<Payout>('POST', '/v1/payouts', options)
  }

  async list(params?: { limit?: number }): Promise<{ data: Payout[]; has_more: boolean }> {
    const path = params?.limit ? `/v1/payouts?limit=${params.limit}` : '/v1/payouts'
    return this.client.request('GET', path)
  }
}

class BalanceClient {
  private client: Gabopay

  constructor(client: Gabopay) {
    this.client = client
  }

  async retrieve(): Promise<Balance> {
    return this.client.request<Balance>('GET', '/v1/balance')
  }
}