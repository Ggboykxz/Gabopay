'use client'

import { Plus, Copy, Trash2, Eye, CheckCircle, XCircle } from 'lucide-react'
import { useState } from 'react'

const webhooks = [
  { id: 'wh_001', url: 'https://api.example.com/webhooks/gabopay', events: ['charge.succeeded', 'charge.failed'], active: true, created: '2024-02-01T00:00:00Z' },
  { id: 'wh_002', url: 'https://example.com/payment-callback', events: ['charge.succeeded'], active: false, created: '2024-03-15T00:00:00Z' },
]

export default function WebhooksPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Webhooks</h1>
          <p className="text-gray-600">Configure webhook endpoints to receive real-time events.</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-gabon-500 text-white rounded-md hover:bg-gabon-600">
          <Plus className="w-4 h-4 mr-2" />
          Add Endpoint
        </button>
      </div>

      <div className="space-y-4">
        {webhooks.map((webhook) => (
          <div key={webhook.id} className="bg-white rounded-lg border p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-gray-900">{webhook.url}</h3>
                  {webhook.active ? (
                    <span className="flex items-center text-xs text-green-600">
                      <CheckCircle className="w-3 h-3 mr-1" /> Active
                    </span>
                  ) : (
                    <span className="flex items-center text-xs text-gray-500">
                      <XCircle className="w-3 h-3 mr-1" /> Inactive
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-500 mt-1 font-mono">{webhook.url}</p>
                <div className="flex gap-2 mt-3">
                  {webhook.events.map((event) => (
                    <span key={event} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                      {event}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                <button className="p-2 text-gray-400 hover:text-gray-600 border rounded">
                  <Eye className="w-4 h-4" />
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600 border rounded">
                  <Copy className="w-4 h-4" />
                </button>
                <button className="p-2 text-red-400 hover:text-red-600 border rounded">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t text-xs text-gray-500">
              Created: {new Date(webhook.created).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}