import { Bell, ChevronDown } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useState } from 'react'

interface TopBarProps { isAdmin?: boolean }

export default function TopBar({ isAdmin }: TopBarProps) {
  const { user, orgs, activeOrgId, setActiveOrg, setAuth } = useAuthStore()
  const [orgOpen, setOrgOpen] = useState(false)

  return (
    <header className={`h-16 flex items-center justify-between px-6 border-b ${
      isAdmin ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-100'
    }`}>
      {/* Left: org switcher */}
      <div className="relative">
        {!isAdmin && orgs.length > 0 && (
          <button
            onClick={() => setOrgOpen((o) => !o)}
            className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            <span>{orgs.find((o) => o.id === activeOrgId)?.name ?? 'Select Org'}</span>
            <ChevronDown size={14} />
          </button>
        )}
        {isAdmin && (
          <span className="text-sm font-semibold text-purple-400 uppercase tracking-widest">Super Admin</span>
        )}
        {orgOpen && (
          <div className="absolute top-8 left-0 z-50 w-56 card py-1 shadow-lg">
            {orgs.map((org) => (
              <button
                key={org.id}
                onClick={() => { setActiveOrg(org.id); setOrgOpen(false) }}
                className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 ${
                  org.id === activeOrgId ? 'text-brand-600 font-semibold' : 'text-gray-700'
                }`}
              >
                {org.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right: user + notifications */}
      <div className="flex items-center gap-4">
        <button className={`p-2 rounded-lg hover:bg-gray-100 ${
          isAdmin ? 'text-gray-400 hover:bg-gray-800' : 'text-gray-500'
        }`}>
          <Bell size={18} />
        </button>
        <div className={`flex items-center gap-2 text-sm ${
          isAdmin ? 'text-gray-300' : 'text-gray-700'
        }`}>
          <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-xs font-bold">
            {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
          </div>
          {user?.full_name}
        </div>
      </div>
    </header>
  )
}
