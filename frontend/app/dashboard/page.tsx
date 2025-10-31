'use client'

import { useQuery } from '@tanstack/react-query'
import { getVerificationStatistics } from '@/lib/api/verification'
import { Users, Building2, Calendar, DollarSign, AlertCircle } from 'lucide-react'

export default function DashboardPage() {
  const { data: stats } = useQuery({
    queryKey: ['verification-stats'],
    queryFn: getVerificationStatistics,
  })

  const cards = [
    {
      title: 'Total Users',
      value: '0',
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Total Properties',
      value: '174',
      icon: Building2,
      color: 'bg-green-500',
    },
    {
      title: 'Active Bookings',
      value: '0',
      icon: Calendar,
      color: 'bg-purple-500',
    },
    {
      title: 'Pending Verifications',
      value: stats?.data?.pending || '0',
      icon: AlertCircle,
      color: 'bg-orange-500',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => {
          const Icon = card.icon
          return (
            <div key={card.title} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{card.title}</p>
                  <p className="text-3xl font-bold mt-2">{card.value}</p>
                </div>
                <div className={`${card.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/dashboard/verification"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <h4 className="font-medium">Review Verifications</h4>
            <p className="text-sm text-gray-600 mt-1">
              {stats?.data?.pending || 0} pending reviews
            </p>
          </a>
          <a
            href="/dashboard/users"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <h4 className="font-medium">Manage Users</h4>
            <p className="text-sm text-gray-600 mt-1">
              View and manage all users
            </p>
          </a>
          <a
            href="/dashboard/analytics"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <h4 className="font-medium">View Analytics</h4>
            <p className="text-sm text-gray-600 mt-1">
              Platform performance metrics
            </p>
          </a>
        </div>
      </div>

      {/* Platform Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Platform Status</h3>
        <div className="space-y-3">
          {[
            { name: 'Host Dashboard', status: 'operational' },
            { name: 'Real Estate Agent Dashboard', status: 'operational' },
            { name: 'Customer AI Platform', status: 'operational' },
          ].map((platform) => (
            <div key={platform.name} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <span className="font-medium">{platform.name}</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600 capitalize">{platform.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

