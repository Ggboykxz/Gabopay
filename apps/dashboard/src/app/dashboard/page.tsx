'use client'

import { ArrowUpRight, ArrowDownRight, CreditCard, DollarSign, Activity } from 'lucide-react'

const stats = [
  {
    title: 'Total Revenue',
    value: '1,250,000 XAF',
    change: '+12.5%',
    changeType: 'positive',
    icon: DollarSign,
  },
  {
    title: 'Transactions',
    value: '156',
    change: '+8.2%',
    changeType: 'positive',
    icon: CreditCard,
  },
  {
    title: 'Success Rate',
    value: '98.2%',
    change: '-0.5%',
    changeType: 'negative',
    icon: Activity,
  },
  {
    title: 'Avg. Transaction',
    value: '8,013 XAF',
    change: '+5.3%',
    changeType: 'positive',
    icon: DollarSign,
  },
]

const chartData = [
  { name: 'Mon', value: 120 },
  { name: 'Tue', value: 180 },
  { name: 'Wed', value: 150 },
  { name: 'Thu', value: 220 },
  { name: 'Fri', value: 280 },
  { name: 'Sat', value: 190 },
  { name: 'Sun', value: 160 },
]
const maxValue = Math.max(...chartData.map(d => d.value))

const recentTransactions = [
  { id: 'ch_001', amount: '15,000 XAF', status: 'succeeded', method: 'Airtel Money', date: '2 min ago' },
  { id: 'ch_002', amount: '8,500 XAF', status: 'succeeded', method: 'Moov Money', date: '15 min ago' },
  { id: 'ch_003', amount: '25,000 XAF', status: 'failed', method: 'Card', date: '1 hour ago' },
  { id: 'ch_004', amount: '5,000 XAF', status: 'pending', method: 'Airtel Money', date: '2 hours ago' },
  { id: 'ch_005', amount: '12,000 XAF', status: 'succeeded', method: 'Moov Money', date: '3 hours ago' },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's an overview of your account.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.title} className="bg-white rounded-lg border p-6">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">{stat.title}</span>
              <stat.icon className="w-5 h-5 text-gray-400" />
            </div>
            <div className="mt-2 flex items-baseline">
              <span className="text-2xl font-bold text-gray-900">{stat.value}</span>
              <span className={`ml-2 text-sm font-medium ${stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
                {stat.changeType === 'positive' ? <ArrowUpRight className="w-4 h-4 inline" /> : <ArrowDownRight className="w-4 h-4 inline" />}
                {' '}{stat.change}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Revenue Overview</h2>
          <div className="h-64 flex items-end justify-between gap-2">
            {chartData.map((item) => (
              <div key={item.name} className="flex-1 flex flex-col items-center gap-2">
                <div 
                  className="w-full bg-gabon-500 rounded-t"
                  style={{ height: `${(item.value / maxValue) * 100}%`, minHeight: '20px' }}
                />
                <span className="text-xs text-gray-500">{item.name}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Transactions</h2>
          <div className="space-y-4">
            {recentTransactions.map((tx) => (
              <div key={tx.id} className="flex items-center justify-between py-3 border-b last:border-0">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${tx.status === 'succeeded' ? 'bg-green-500' : tx.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'}`} />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{tx.amount}</p>
                    <p className="text-xs text-gray-500">{tx.method}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-xs font-medium ${tx.status === 'succeeded' ? 'text-green-600' : tx.status === 'failed' ? 'text-red-600' : 'text-yellow-600'}`}>
                    {tx.status}
                  </p>
                  <p className="text-xs text-gray-500">{tx.date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}