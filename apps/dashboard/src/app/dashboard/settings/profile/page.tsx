'use client'

import { User, Mail, Phone, Building } from 'lucide-react'

export default function ProfilePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <p className="text-gray-600">Manage your account information.</p>
      </div>

      <div className="bg-white rounded-lg border p-6 space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 bg-gabon-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
            M
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Merchant Name</h2>
            <p className="text-sm text-gray-600">Active Account</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Business Name</label>
            <div className="flex items-center border rounded-md px-3 py-2 bg-gray-50">
              <Building className="w-4 h-4 text-gray-400 mr-2" />
              <span className="text-gray-900">My Business Ltd</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <div className="flex items-center border rounded-md px-3 py-2 bg-gray-50">
              <Mail className="w-4 h-4 text-gray-400 mr-2" />
              <span className="text-gray-900">merchant@example.com</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
            <div className="flex items-center border rounded-md px-3 py-2 bg-gray-50">
              <Phone className="w-4 h-4 text-gray-400 mr-2" />
              <span className="text-gray-900">+241 77 123 456</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
            <div className="flex items-center border rounded-md px-3 py-2 bg-gray-50">
              <span className="text-gray-900">Gabon (GA)</span>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <button className="px-4 py-2 border rounded-md hover:bg-gray-50">Cancel</button>
          <button className="px-4 py-2 bg-gabon-500 text-white rounded-md hover:bg-gabon-600">Save Changes</button>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-yellow-800">KYC Verification</h3>
        <p className="text-sm text-yellow-700 mt-1">
          Complete your KYC verification to unlock full features.
        </p>
        <button className="mt-2 px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 text-sm">
          Complete KYC
        </button>
      </div>
    </div>
  )
}