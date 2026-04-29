import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const api = axios.create({
  // In dev, Vite proxies /api → http://localhost:8000
  // In prod, set VITE_API_URL and update baseURL accordingly
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT + org header on every request
api.interceptors.request.use((config) => {
  const { token, activeOrgId } = useAuthStore.getState()
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  if (activeOrgId) config.headers['X-Org-Id'] = activeOrgId
  return config
})

// Auto-logout on 401 — but only if we were previously authenticated
// to avoid a loop on the /login and /register pages
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const isAuthEndpoint =
      err.config?.url?.includes('/auth/login') ||
      err.config?.url?.includes('/auth/register')
    if (err.response?.status === 401 && !isAuthEndpoint) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
