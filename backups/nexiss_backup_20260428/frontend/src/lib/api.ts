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
  if (activeOrgId) config.headers['X-Org-Id'] = activeOrgId
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
