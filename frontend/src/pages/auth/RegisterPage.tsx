import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/authStore'
import toast from 'react-hot-toast'

function toSlug(str: string): string {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    org_name: '',
    org_slug: '',
  })
  const [slugEdited, setSlugEdited] = useState(false)
  const [loading, setLoading] = useState(false)

  // Auto-fill slug from org name unless user has manually edited it
  const handleOrgName = (val: string) => {
    setForm((f) => ({ ...f, org_name: val, org_slug: slugEdited ? f.org_slug : toSlug(val) }))
  }

  const handle = async (e: React.FormEvent) => {
    e.preventDefault()
    const slug = toSlug(form.org_slug || form.org_name)
    if (!slug) {
      toast.error('Organisation name / slug is required')
      return
    }
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      // Register returns a token directly (same as login)
      const { data: regData } = await authApi.register({ ...form, org_slug: slug })

      // Store token first so /me can authenticate
      useAuthStore.setState({ token: regData.access_token })

      // Fetch user profile
      const { data: user } = await authApi.me()
      setAuth(regData.access_token, user)

      toast.success('Account created!')
      navigate(user.is_superuser ? '/admin' : '/app')
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      const msg = Array.isArray(detail)
        ? detail.map((d: any) => d.msg).join(', ')
        : typeof detail === 'string'
        ? detail
        : 'Registration failed. Please check your inputs.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const f =
    (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm({ ...form, [k]: e.target.value })

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Create account</h1>
      <p className="text-sm text-gray-500 mb-6">Start turning documents into data</p>
      <form onSubmit={handle} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Full name</label>
            <input
              required
              className="input"
              placeholder="Jane Doe"
              value={form.full_name}
              onChange={f('full_name')}
              autoComplete="name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Organisation</label>
            <input
              required
              className="input"
              placeholder="Acme Ltd"
              value={form.org_name}
              onChange={(e) => handleOrgName(e.target.value)}
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Organisation ID <span className="text-gray-400 font-normal">(auto-filled, lowercase only)</span>
          </label>
          <input
            required
            className="input font-mono text-sm"
            placeholder="acme-ltd"
            value={form.org_slug}
            onChange={(e) => { setSlugEdited(true); setForm({ ...form, org_slug: toSlug(e.target.value) }) }}
            pattern="^[a-z0-9-]+$"
            title="Lowercase letters, numbers and hyphens only"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="email"
            required
            className="input"
            placeholder="you@company.com"
            value={form.email}
            onChange={f('email')}
            autoComplete="email"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            type="password"
            required
            minLength={8}
            className="input"
            placeholder="Min 8 characters"
            value={form.password}
            onChange={f('password')}
            autoComplete="new-password"
          />
        </div>
        <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
          {loading ? 'Creating account...' : 'Create account'}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-gray-500">
        Already have an account?{' '}
        <a href="/login" className="text-brand-600 font-medium hover:underline">Sign in</a>
      </p>
    </div>
  )
}
