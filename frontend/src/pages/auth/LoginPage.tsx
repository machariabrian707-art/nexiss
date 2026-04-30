import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/authStore'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)

  const handle = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      // Step 1: get token
      const { data: loginData } = await authApi.login(form)

      // Step 2: store token FIRST so the /me request gets the Authorization header
      // We store a temporary user object; it gets replaced in step 3
      useAuthStore.setState({ token: loginData.access_token })

      // Step 3: now fetch the full user profile (token is in the store now)
      const { data: user } = await authApi.me()

      // Step 4: setAuth stores token + user + derives activeOrgId from user.active_org_id
      setAuth(loginData.access_token, user)

      toast.success('Welcome back!')
      navigate(user.is_superuser ? '/admin' : '/app')
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Invalid email or password'
      toast.error(typeof msg === 'string' ? msg : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Sign in</h1>
      <p className="text-sm text-gray-500 mb-6">Enter your credentials to continue</p>
      <form onSubmit={handle} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="email"
            required
            className="input"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="you@company.com"
            autoComplete="email"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            type="password"
            required
            className="input"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="••••••••"
            autoComplete="current-password"
          />
        </div>
        <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-gray-500">
        No account?{' '}
        <a href="/register" className="text-brand-600 font-medium hover:underline">Create one</a>
      </p>
    </div>
  )
}
