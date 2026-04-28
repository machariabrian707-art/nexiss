import api from '@/lib/api'
import type { AuthUser } from '@/stores/authStore'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { email: string; password: string; full_name: string; org_name: string; org_slug: string }

export const authApi = {
  login: (data: LoginPayload) =>
    api.post<{ access_token: string }>('/auth/login', data),

  register: (data: RegisterPayload) =>
    api.post('/auth/register', data),

  // Returns is_superuser (matches backend User model)
  me: () =>
    api.get<AuthUser>('/auth/me'),

  switchOrg: (org_id: string) =>
    api.post<{ access_token: string }>('/auth/switch-org', { org_id }),
}
