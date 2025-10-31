import apiClient from './client'

export interface User {
  id: string
  email: string
  platform_id: string
  platform_user_id: string
  user_type: 'host' | 'agent' | 'customer' | 'guest'
  full_name?: string
  phone?: string
  verification_status?: string
  account_status: 'active' | 'suspended' | 'banned'
  last_synced_at?: string
  created_at: string
}

export interface UsersListParams {
  platform?: string
  user_type?: string
  account_status?: string
  search?: string
  page?: number
  limit?: number
}

export async function getUsers(params: UsersListParams = {}) {
  const response = await apiClient.get('/api/v1/users', { params })
  return response.data
}

export async function getUser(userId: string) {
  const response = await apiClient.get(`/api/v1/users/${userId}`)
  return response.data
}

export async function updateUserStatus(
  userId: string,
  status: 'active' | 'suspended' | 'banned',
  reason?: string
) {
  const response = await apiClient.patch(`/api/v1/users/${userId}/status`, {
    status,
    reason,
  })
  return response.data
}

