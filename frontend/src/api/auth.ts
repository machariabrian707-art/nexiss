import api from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'

const BASE = '/api/v1'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  org_name: string
  org_slug: string
}

export const authApi = {
  login: (data: LoginPayload) =>
    api.post<{ access_token: string; token_type: string; expires_in_seconds: number }>(
      '/auth/login', data
    ),

  register: (data: RegisterPayload) =>
    api.post<{ access_token: string; token_type: string; expires_in_seconds: number }>(
      '/auth/register', data
    ),

  // Must be called AFTER token is stored in the auth store
  me: () => {
    const { token, activeOrgId } = useAuthStore.getState()
    return api.get('/auth/me', {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        // X-Org-Id is only needed for org-scoped endpoints, not /me
      },
    })
  },

  switchOrg: (org_id: string) =>
    api.post<{ access_token: string }>('/auth/switch-org', { org_id }),
}
