import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { authApi } from '@/api/auth'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: '', email: '', password: '', org_name: '' })
  const [loading, setLoading] = useState(false)

  const handle = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await authApi.register(form)
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } catch {
      toast.error('Registration failed. Email may already be in use.')
    } finally {
      setLoading(false)
    }
  }

  const f = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value })

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Create account</h1>
      <p className="text-sm text-gray-500 mb-6">Start turning documents into data</p>
      <form onSubmit={handle} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Full name</label>
            <input required className="input" placeholder="Jane Doe" value={form.full_name} onChange={f('full_name')} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Organisation</label>
            <input required className="input" placeholder="Acme Ltd" value={form.org_name} onChange={f('org_name')} />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input type="email" required className="input" placeholder="you@company.com" value={form.email} onChange={f('email')} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input type="password" required className="input" placeholder="Min 8 characters" value={form.password} onChange={f('password')} />
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
