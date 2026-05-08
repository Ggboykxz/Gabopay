/**
 * GABOPAY Webhooks
 */

import crypto from 'crypto'
import type { WebhookEvent } from './types'
import { WebhookVerificationError } from './errors'

export class Webhooks {
  constructEvent(
    payload: string | object,
    signature: string,
    secret: string
  ): WebhookEvent {
    if (!signature) {
      throw new WebhookVerificationError('Signature is required')
    }

    if (!secret) {
      throw new WebhookVerificationError('Secret is required')
    }

    const payloadStr = typeof payload === 'string' ? payload : JSON.stringify(payload)

    if (!this.verifySignature(payloadStr, signature, secret)) {
      throw new WebhookVerificationError('Invalid signature')
    }

    const parsed = typeof payload === 'string' ? JSON.parse(payload) : payload

    return parsed as WebhookEvent
  }

  verifySignature(
    payload: string,
    signature: string,
    secret: string
  ): boolean {
    try {
      const parts = signature.split(',')
      const params: Record<string, string> = {}

      for (const part of parts) {
        const [key, value] = part.split('=')
        if (key && value) {
          params[key] = value
        }
      }

      const timestamp = parseInt(params['t'] || '0', 10)
      const expectedSignature = params['v1']

      if (!timestamp || !expectedSignature) {
        return false
      }

      const currentTime = Math.floor(Date.now() / 1000)
      const tolerance = 300

      if (Math.abs(currentTime - timestamp) > tolerance) {
        return false
      }

      const signedPayload = `${timestamp}.${payload}`
      const computedSignature = crypto
        .createHmac('sha256', secret)
        .update(signedPayload)
        .digest('hex')

      return crypto.timingSafeEqual(
        Buffer.from(computedSignature),
        Buffer.from(expectedSignature)
      )
    } catch {
      return false
    }
  }
}