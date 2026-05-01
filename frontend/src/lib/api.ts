import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT + org header on every request
api.interceptors.request.use((config) => {
  const { token, activeOrgId } = useAuthStore.getState()
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  // Only send X-Org-Id when we have one AND the endpoint is not an auth endpoint
  const isAuthEndpoint = config.url?.startsWith('/auth/')
  if (activeOrgId && !isAuthEndpoint) {
    config.headers['X-Org-Id'] = activeOrgId
  }
  return config
})

// Auto-logout on 401 for non-auth endpoints
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const isAuthEndpoint =
      err.config?.url?.includes('/auth/login') ||
      err.config?.url?.includes('/auth/register') ||
      err.config?.url?.includes('/auth/me')
    if (err.response?.status === 401 && !isAuthEndpoint) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
