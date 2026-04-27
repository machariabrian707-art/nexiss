import { useAuthStore } from '@/stores/authStore'
import { User, Building2, Key } from 'lucide-react'

export default function SettingsPage() {
  const { user, orgs, activeOrgId } = useAuthStore()
  const activeOrg = orgs.find((o) => o.id === activeOrgId)

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500 mt-1">Manage your profile and organisation</p>
      </div>

      {/* Profile */}
      <div className="card p-6 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <User size={16} className="text-gray-400" />
          <h2 className="font-semibold text-gray-800">Profile</h2>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Full Name</label>
            <input className="input" defaultValue={user?.full_name ?? ''} readOnly />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Email</label>
            <input className="input" defaultValue={user?.email ?? ''} readOnly />
          </div>
        </div>
      </div>

      {/* Organisation */}
      <div className="card p-6 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <Building2 size={16} className="text-gray-400" />
          <h2 className="font-semibold text-gray-800">Organisation</h2>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Name</label>
            <input className="input" defaultValue={activeOrg?.name ?? ''} readOnly />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Slug</label>
            <input className="input" defaultValue={activeOrg?.slug ?? ''} readOnly />
          </div>
        </div>
      </div>

      {/* API */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Key size={16} className="text-gray-400" />
          <h2 className="font-semibold text-gray-800">API Access</h2>
        </div>
        <p className="text-sm text-gray-500 mb-3">
          Use the Nexiss API to programmatically upload and query documents.
        </p>
        <div className="bg-gray-900 rounded-xl px-4 py-3 text-xs text-green-300 font-mono">
          POST /api/v1/documents<br />
          GET  /api/v1/documents/:id<br />
          GET  /api/v1/analytics/overview
        </div>
      </div>
    </div>
  )
}
