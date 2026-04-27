import api from '@/lib/api'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { email: string; password: string; full_name: string; org_name: string }

export const authApi = {
  login: (data: LoginPayload) =>
    api.post<{ access_token: string }>('/auth/login', data),

  register: (data: RegisterPayload) =>
    api.post('/auth/register', data),

  me: () =>
    api.get<{ id: string; email: string; full_name: string; is_superadmin: boolean }>('/auth/me'),

  switchOrg: (org_id: string) =>
    api.post<{ access_token: string }>('/auth/switch-org', { org_id }),
}
