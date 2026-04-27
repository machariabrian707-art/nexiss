import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, FileText, Upload, BarChart2,
  Search, Settings, LogOut, ChevronLeft, ChevronRight, ShieldAlert
} from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import clsx from 'clsx'

const navItems = [
  { to: '/app',           icon: LayoutDashboard, label: 'Dashboard',   end: true },
  { to: '/app/documents', icon: FileText,         label: 'Documents' },
  { to: '/app/upload',    icon: Upload,           label: 'Upload' },
  { to: '/app/analytics', icon: BarChart2,        label: 'Analytics' },
  { to: '/app/search',    icon: Search,           label: 'Search' },
  { to: '/app/settings',  icon: Settings,         label: 'Settings' },
]

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <aside
      className={clsx(
        'fixed inset-y-0 left-0 z-40 flex flex-col bg-white border-r border-gray-100 shadow-sm transition-all duration-300',
        sidebarOpen ? 'w-64' : 'w-16'
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-gray-100">
        {sidebarOpen && (
          <span className="text-xl font-bold text-brand-600 tracking-tight">Nexiss</span>
        )}
        <button
          onClick={toggleSidebar}
          className="ml-auto p-1.5 rounded-lg hover:bg-gray-100 text-gray-500"
        >
          {sidebarOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {navItems.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              )
            }
          >
            <Icon size={18} className="shrink-0" />
            {sidebarOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-2 border-t border-gray-100 space-y-1">
        {user?.is_superadmin && (
          <NavLink
            to="/admin"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-purple-600 hover:bg-purple-50 transition-colors"
          >
            <ShieldAlert size={18} className="shrink-0" />
            {sidebarOpen && <span>Admin Panel</span>}
          </NavLink>
        )}
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
        >
          <LogOut size={18} className="shrink-0" />
          {sidebarOpen && <span>Logout</span>}
        </button>
      </div>
    </aside>
  )
}
