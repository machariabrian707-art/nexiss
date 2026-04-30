import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, Building2, FileText,
  BarChart2, CreditCard, Server, LogOut,
  ChevronLeft, ChevronRight, ArrowLeft
} from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import clsx from 'clsx'

const adminNav = [
  { to: '/admin',           icon: LayoutDashboard, label: 'Overview',  end: true },
  { to: '/admin/orgs',      icon: Building2,       label: 'Organisations' },
  { to: '/admin/users',     icon: Users,           label: 'Users' },
  { to: '/admin/documents', icon: FileText,        label: 'Documents' },
  { to: '/admin/analytics', icon: BarChart2,       label: 'Analytics' },
  { to: '/admin/billing',   icon: CreditCard,      label: 'Billing' },
  { to: '/admin/system',    icon: Server,          label: 'System' },
]

export default function AdminSidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { logout } = useAuthStore()
  const navigate = useNavigate()

  return (
    <aside
      className={clsx(
        'fixed inset-y-0 left-0 z-40 flex flex-col bg-gray-900 transition-all duration-300',
        sidebarOpen ? 'w-64' : 'w-16'
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-gray-700">
        {sidebarOpen && (
          <div>
            <span className="text-lg font-bold text-white">Nexiss</span>
            <span className="ml-2 text-xs text-purple-400 font-semibold uppercase tracking-widest">Admin</span>
          </div>
        )}
        <button
          onClick={toggleSidebar}
          className="ml-auto p-1.5 rounded-lg hover:bg-gray-800 text-gray-400"
        >
          {sidebarOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {adminNav.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              )
            }
          >
            <Icon size={18} className="shrink-0" />
            {sidebarOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-2 border-t border-gray-700 space-y-1">
        <button
          onClick={() => navigate('/app')}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <ArrowLeft size={18} className="shrink-0" />
          {sidebarOpen && <span>Back to App</span>}
        </button>
        <button
          onClick={() => { logout(); navigate('/login') }}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut size={18} className="shrink-0" />
          {sidebarOpen && <span>Logout</span>}
        </button>
      </div>
    </aside>
  )
}
