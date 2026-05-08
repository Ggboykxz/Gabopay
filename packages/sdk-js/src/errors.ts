/**
 * GABOPAY SDK Errors
 */

export class GabopayError extends Error {
  statusCode?: number
  code?: string

  constructor(message: string, statusCode?: number, code?: string) {
    super(message)
    this.name = 'GabopayError'
    this.statusCode = statusCode
    this.code = code
  }
}

export class WebhookVerificationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'WebhookVerificationError'
  }
}