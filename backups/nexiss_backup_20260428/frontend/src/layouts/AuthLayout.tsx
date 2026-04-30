import { Outlet } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-900 via-brand-800 to-brand-600 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="mb-8 text-center">
          <span className="text-3xl font-bold text-white tracking-tight">Nexiss</span>
          <p className="mt-1 text-brand-200 text-sm">Document Intelligence Platform</p>
        </div>
        <div className="card p-8">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
