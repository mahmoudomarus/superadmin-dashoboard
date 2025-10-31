import apiClient from './client'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    email: string
    full_name: string
    role: string
  }
}

export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post('/api/v1/auth/login', credentials)
  return response.data
}

export async function getCurrentUser() {
  const response = await apiClient.get('/api/v1/auth/me')
  return response.data
}

export function logout() {
  localStorage.removeItem('access_token')
  window.location.href = '/login'
}

