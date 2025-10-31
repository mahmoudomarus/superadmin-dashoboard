import apiClient from './client'

export interface VerificationItem {
  id: string
  platform_id: string
  user_id: string
  platform_user_id: string
  verification_type: string
  status: 'pending' | 'in_review' | 'approved' | 'rejected'
  documents: any
  created_at: string
  updated_at: string
}

export async function getVerificationQueue(status: string = 'pending') {
  const response = await apiClient.get('/api/v1/verification/queue', {
    params: { status },
  })
  return response.data
}

export async function getVerificationDetails(verificationId: string) {
  const response = await apiClient.get(`/api/v1/verification/${verificationId}`)
  return response.data
}

export async function approveVerification(verificationId: string, notes: string) {
  const response = await apiClient.post(
    `/api/v1/verification/${verificationId}/approve`,
    { notes }
  )
  return response.data
}

export async function rejectVerification(
  verificationId: string,
  reason: string,
  notes?: string
) {
  const response = await apiClient.post(
    `/api/v1/verification/${verificationId}/reject`,
    { reason, notes }
  )
  return response.data
}

export async function getVerificationStatistics() {
  const response = await apiClient.get('/api/v1/verification/statistics')
  return response.data
}

