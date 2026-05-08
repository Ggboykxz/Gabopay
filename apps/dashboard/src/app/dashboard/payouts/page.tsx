'use client'

import { Wallet, ArrowUpRight } from 'lucide-react'

const payouts = [
  { id: 'po_001', amount: 50000, method: 'airtel_money', phone: '+24177****01', status: 'succeeded', created: '2024-05-07T10:00:00Z' },
  { id: 'po_002', amount: 25000, method: 'moov_money', phone: '+24174****02', status: 'succeeded', created: '2024-05-06T14:30:00Z' },
  { id: 'po_003', amount: 100000, method: 'airtel_money', phone: '+24176****03', status: 'pending', created: '2024-05-08T09:00:00Z' },
]

export default function PayoutsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payouts</h1>
          <p className="text-gray-600">Withdraw funds to your mobile money account.</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-gabon-500 text-white rounded-md hover:bg-gabon-600">
          <ArrowUpRight className="w-4 h-4 mr-2" />
          Request Payout
        </button>
      </div>

      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gabon-50 rounded-lg">
            <Wallet className="w-6 h-6 text-gabon-500" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Available Balance</p>
            <p className="text-2xl font-bold text-gray-900">850,000 XAF</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {payouts.map((payout) => (
              <tr key={payout.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <span className="font-mono text-sm text-gray-900">{payout.id}</span>
                </td>
                <td className="px-6 py-4">
                  <span className="font-medium text-gray-900">{payout.amount.toLocaleString()} XAF</span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{payout.method.replace('_', ' ')}</td>
                <td className="px-6 py-4 font-mono text-sm text-gray-600">{payout.phone}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    payout.status === 'succeeded' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {payout.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{new Date(payout.created).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}