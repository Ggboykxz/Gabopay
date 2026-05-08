'use client'

import { Plus, Copy, Trash2, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'

const apiKeys = [
  { id: 'key_001', name: 'Production Key', prefix: 'gp_live', lastUsed: '2024-05-08T10:30:00Z', created: '2024-01-15T00:00:00Z' },
  { id: 'key_002', name: 'Test Key', prefix: 'gp_test', lastUsed: '2024-05-07T18:00:00Z', created: '2024-01-15T00:00:00Z' },
]

export default function ApiKeysPage() {
  const [showKey, setShowKey] = useState<string | null>(null)
  const [copied, setCopied] = useState<string | null>(null)

  const copyKey = (key: string) => {
    navigator.clipboard.writeText(key)
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">API Keys</h1>
          <p className="text-gray-600">Manage your API keys for accessing the GABOPAY API.</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-gabon-500 text-white rounded-md hover:bg-gabon-600">
          <Plus className="w-4 h-4 mr-2" />
          Create API Key
        </button>
      </div>

      <div className="bg-white rounded-lg border">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Key</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mode</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Used</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {apiKeys.map((key) => (
              <tr key={key.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <span className="font-medium text-gray-900">{key.name}</span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <code className="font-mono text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded">
                      {showKey === key.id ? `${key.prefix}_xxxxxx` : `${key.prefix}_sk_••••••••`}
                    </code>
                    <button onClick={() => setShowKey(showKey === key.id ? null : key.id)} className="text-gray-400 hover:text-gray-600">
                      {showKey === key.id ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                    <button onClick={() => copyKey(`${key.prefix}_sk_real_key_here`)} className="text-gray-400 hover:text-gray-600">
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${key.prefix === 'gp_live' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {key.prefix === 'gp_live' ? 'Live' : 'Test'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{new Date(key.lastUsed).toLocaleDateString()}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{new Date(key.created).toLocaleDateString()}</td>
                <td className="px-6 py-4">
                  <button className="text-red-500 hover:text-red-700">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800">Security Notice</h3>
        <p className="text-sm text-blue-700 mt-1">
          Never share your API keys in public repositories or client-side code. Store them securely on your server.
        </p>
      </div>
    </div>
  )
}