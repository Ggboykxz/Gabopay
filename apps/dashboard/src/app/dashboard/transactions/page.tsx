'use client'

import { Search, Filter, Download, RefreshCw } from 'lucide-react'
import { useState } from 'react'

const transactions = [
  { id: 'ch_01J7ABC123', amount: 15000, currency: 'XAF', status: 'succeeded', method: 'airtel_money', phone: '+24177****01', created: '2024-05-08T10:30:00Z' },
  { id: 'ch_01J7ABC124', amount: 8500, currency: 'XAF', status: 'succeeded', method: 'moov_money', phone: '+24174****02', created: '2024-05-08T09:15:00Z' },
  { id: 'ch_01J7ABC125', amount: 25000, currency: 'XAF', status: 'failed', method: 'card', phone: null, created: '2024-05-08T08:45:00Z' },
  { id: 'ch_01J7ABC126', amount: 5000, currency: 'XAF', status: 'pending', method: 'airtel_money', phone: '+24176****03', created: '2024-05-07T22:00:00Z' },
  { id: 'ch_01J7ABC127', amount: 12000, currency: 'XAF', status: 'succeeded', method: 'moov_money', phone: '+24175****04', created: '2024-05-07T18:30:00Z' },
  { id: 'ch_01J7ABC128', amount: 3500, currency: 'XAF', status: 'refunded', method: 'card', phone: null, created: '2024-05-07T15:20:00Z' },
  { id: 'ch_01J7ABC129', amount: 45000, currency: 'XAF', status: 'succeeded', method: 'airtel_money', phone: '+24177****05', created: '2024-05-07T12:00:00Z' },
  { id: 'ch_01J7ABC130', amount: 20000, currency: 'XAF', status: 'failed', method: 'moov_money', phone: '+24174****06', created: '2024-05-07T10:45:00Z' },
]

export default function TransactionsPage() {
  const [statusFilter, setStatusFilter] = useState('all')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
          <p className="text-gray-600">View and manage all your payment transactions.</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center px-4 py-2 border rounded-md hover:bg-gray-50 text-sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button className="flex items-center px-4 py-2 border rounded-md hover:bg-gray-50 text-sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync
          </button>
        </div>
      </div>

      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search transactions..."
            className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-gabon-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-gabon-500"
        >
          <option value="all">All Status</option>
          <option value="succeeded">Succeeded</option>
          <option value="failed">Failed</option>
          <option value="pending">Pending</option>
          <option value="refunded">Refunded</option>
        </select>
      </div>

      <div className="bg-white rounded-lg border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {transactions.map((tx) => (
              <tr key={tx.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-mono text-sm text-gray-900">{tx.id}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-medium text-gray-900">{tx.amount.toLocaleString()} {tx.currency}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-600">{tx.method.replace('_', ' ')}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    tx.status === 'succeeded' ? 'bg-green-100 text-green-800' :
                    tx.status === 'failed' ? 'bg-red-100 text-red-800' :
                    tx.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {tx.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-mono text-sm text-gray-600">{tx.phone || '—'}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-500">{new Date(tx.created).toLocaleString()}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">Showing 8 of 156 transactions</p>
        <div className="flex gap-2">
          <button className="px-4 py-2 border rounded-md hover:bg-gray-50 text-sm" disabled>Previous</button>
          <button className="px-4 py-2 border rounded-md hover:bg-gray-50 text-sm">Next</button>
        </div>
      </div>
    </div>
  )
}