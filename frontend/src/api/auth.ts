import api from '@/lib/api'
import type { AuthUser } from '@/stores/authStore'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  org_name: string
  org_slug: string   // must match ^[a-z0-9-]+$ (backend validation)
}

export const authApi = {
  login: (data: LoginPayload) =>
    api.post<{ access_token: string; token_type: string; expires_in_seconds: number }>('/auth/login', data),

  register: (data: RegisterPayload) =>
    api.post<{ access_token: string; token_type: string; expires_in_seconds: number }>('/auth/register', data),

  // Uses Authorization header — must be called AFTER token is stored
  me: () =>
    api.get<AuthUser>('/auth/me'),

  switchOrg: (org_id: string) =>
    api.post<{ access_token: string }>('/auth/switch-org', { org_id }),
}
