'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getVerificationQueue,
  getVerificationDetails,
  approveVerification,
  rejectVerification,
} from '@/lib/api/verification'
import { format } from 'date-fns'
import { CheckCircle, XCircle, Clock, Eye } from 'lucide-react'

export default function VerificationPage() {
  const queryClient = useQueryClient()
  const [selectedStatus, setSelectedStatus] = useState('pending')
  const [selectedVerification, setSelectedVerification] = useState<string | null>(null)

  const { data: queue, isLoading } = useQuery({
    queryKey: ['verification-queue', selectedStatus],
    queryFn: () => getVerificationQueue(selectedStatus),
  })

  const { data: details } = useQuery({
    queryKey: ['verification-details', selectedVerification],
    queryFn: () => getVerificationDetails(selectedVerification!),
    enabled: !!selectedVerification,
  })

  const approveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) =>
      approveVerification(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['verification-queue'] })
      setSelectedVerification(null)
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      rejectVerification(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['verification-queue'] })
      setSelectedVerification(null)
    },
  })

  const handleApprove = (id: string) => {
    const notes = prompt('Enter approval notes:')
    if (notes) {
      approveMutation.mutate({ id, notes })
    }
  }

  const handleReject = (id: string) => {
    const reason = prompt('Enter rejection reason:')
    if (reason) {
      rejectMutation.mutate({ id, reason })
    }
  }

  return (
    <div className="space-y-6">
      {/* Status Filter */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex space-x-2">
          {['pending', 'in_review', 'approved', 'rejected', 'all'].map((status) => (
            <button
              key={status}
              onClick={() => setSelectedStatus(status)}
              className={`px-4 py-2 rounded-lg capitalize ${
                selectedStatus === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Verification Queue */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Verification Queue</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {isLoading ? (
            <div className="p-6 text-center text-gray-500">Loading...</div>
          ) : queue?.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No verifications in this status
            </div>
          ) : (
            queue?.map((item: any) => (
              <div
                key={item.id}
                className="p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="font-medium">{item.verification_type}</span>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          item.status === 'approved'
                            ? 'bg-green-100 text-green-700'
                            : item.status === 'rejected'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Platform User ID: {item.platform_user_id}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Submitted: {format(new Date(item.created_at), 'PPP')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {item.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleApprove(item.id)}
                          className="p-2 text-green-600 hover:bg-green-50 rounded-lg"
                          title="Approve"
                        >
                          <CheckCircle className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleReject(item.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          title="Reject"
                        >
                          <XCircle className="w-5 h-5" />
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => setSelectedVerification(item.id)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                      title="View Details"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Details Modal (simplified) */}
      {selectedVerification && details && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Verification Details</h3>
            </div>
            <div className="p-6">
              <pre className="text-sm bg-gray-50 p-4 rounded overflow-auto">
                {JSON.stringify(details, null, 2)}
              </pre>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => setSelectedVerification(null)}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

