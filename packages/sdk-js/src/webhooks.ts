/**
 * GABOPAY Webhooks
 */

import type { WebhookEvent } from './types'
import { WebhookVerificationError } from './errors'

interface HmacLike {
  update(data: string): HmacLike
  digest(): string
}

function createHmac(secret: string): HmacLike {
  if (typeof process !== 'undefined' && process.versions?.node) {
    const crypto = require('crypto')
    const hmac = crypto.createHmac('sha256', secret)
    return {
      update(data: string) {
        hmac.update(data)
        return this
      },
      digest() {
        return hmac.digest('hex')
      }
    }
  }

  const encoder = new TextEncoder()
  let _data = ''

  return {
    update(data: string) {
      _data = data
      return this
    },
    digest() {
      const key = encoder.encode(secret)
      const msg = encoder.encode(_data)
      let result = ''
      crypto.subtle.importKey('raw', key, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
        .then((k: CryptoKey) => crypto.subtle.sign('HMAC', k, msg))
        .then((sig: ArrayBuffer) => {
          result = Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, '0')).join('')
        })
      return result
    }
  }
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) {
    let result = a.length ^ b.length
    for (let i = 0; i < Math.min(a.length, b.length); i++) {
      result |= a.charCodeAt(i) ^ b.charCodeAt(i)
    }
    return result === 0
  }
  let result = 0
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i)
  }
  return result === 0
}

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
      const hmac = createHmac(secret)
      hmac.update(signedPayload)
      const computedSignature = hmac.digest()

      return timingSafeEqual(computedSignature, expectedSignature)
    } catch {
      return false
    }
  }
}
