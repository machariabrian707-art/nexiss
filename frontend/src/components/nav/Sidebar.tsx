import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, FileText, Upload, BarChart2,
  Search, Settings, LogOut, ShieldAlert, Cpu
} from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import { canProcessDocuments, isSuperadmin } from '@/lib/permissions'
import clsx from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'
import { motionTokens } from '@/lib/motion'

const navItems = [
  { to: '/app',           icon: LayoutDashboard, label: 'Hub',   end: true },
  { to: '/app/documents', icon: FileText,         label: 'Repository' },
  { to: '/app/analytics', icon: BarChart2,        label: 'Intelligence' },
  { to: '/app/search',    icon: Search,           label: 'Discovery' },
  { to: '/app/settings',  icon: Settings,         label: 'Core' },
]

export default function Sidebar() {
  const { sidebarOpen } = useUIStore()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const navForRole = canProcessDocuments(user)
    ? [...navItems.slice(0, 2), { to: '/app/upload', icon: Upload, label: 'Ingest' }, ...navItems.slice(2)]
    : navItems

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <motion.aside
      initial={{ x: -40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: motionTokens.duration.base, ease: motionTokens.ease.entrance }}
      className={clsx(
        'relative h-screen z-40 flex flex-col transition-all duration-500 ease-in-out',
        sidebarOpen ? 'w-64' : 'w-24'
      )}
      style={{ willChange: 'transform, opacity' }}
    >
      <div className="h-full py-6 px-4">
        <div className="h-full glass rounded-3xl flex flex-col shadow-2xl border-white/5">
          {/* Logo Section */}
          <div className="flex flex-col items-center py-8">
            <div className="relative">
              <div className="absolute inset-0 bg-brand-400 blur-xl opacity-20 animate-pulse" />
              <div className="relative bg-gradient-to-br from-brand-400 to-accent-indigo p-2.5 rounded-2xl shadow-glow-brand">
                <Cpu size={24} className="text-white" />
              </div>
            </div>
            <AnimatePresence>
              {sidebarOpen && (
                <motion.span
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="mt-4 text-xl font-bold font-lexend tracking-tighter bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent"
                >
                  NEXISS
                </motion.span>
              )}
            </AnimatePresence>
          </div>

          {/* Navigation */}
          <motion.nav
            initial="hidden"
            animate="visible"
            variants={{
              hidden: {},
              visible: { transition: { staggerChildren: 0.05 } },
            }}
            className="flex-1 px-3 py-6 space-y-2"
          >
            {navForRole.map(({ to, icon: Icon, label, end }) => (
              <motion.div key={to} variants={{ hidden: { opacity: 0, x: -12 }, visible: { opacity: 1, x: 0 } }}>
                <NavLink
                  to={to}
                  end={end}
                  className={({ isActive }) =>
                    clsx(
                      'group relative flex items-center gap-4 px-4 py-3 rounded-2xl text-sm font-medium transition-all duration-300',
                      isActive
                        ? 'bg-white/10 text-brand-400 shadow-inner'
                        : 'text-gray-500 hover:text-gray-200 hover:bg-white/5'
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      <Icon size={20} className={clsx('shrink-0 transition-transform duration-300 group-hover:scale-[1.08]', isActive && 'text-brand-400')} />
                      {sidebarOpen && (
                        <motion.span
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="truncate font-lexend"
                        >
                          {label}
                        </motion.span>
                      )}
                      {isActive && (
                        <>
                          <motion.div
                            layoutId="activeNav"
                            className="absolute left-0 w-1 bg-brand-400 rounded-r-full shadow-glow-brand"
                            initial={{ height: 0 }}
                            animate={{ height: 26 }}
                            transition={{ duration: motionTokens.duration.fast }}
                          />
                          <motion.div
                            className="absolute inset-0 rounded-2xl bg-brand-400/10 pointer-events-none"
                            animate={{ opacity: [0.6, 1, 0.6] }}
                            transition={{ duration: 1.4, repeat: Infinity, ease: 'easeInOut' }}
                          />
                        </>
                      )}
                    </>
                  )}
                </NavLink>
              </motion.div>
            ))}
          </motion.nav>

          {/* User Section */}
          <div className="p-3 border-t border-white/5 space-y-2">
            {isSuperadmin(user) && (
              <NavLink
                to="/admin"
                className="flex items-center gap-4 px-4 py-3 rounded-2xl text-sm font-medium text-accent-indigo hover:bg-white/5 transition-all"
              >
                <ShieldAlert size={20} className="shrink-0" />
                {sidebarOpen && <span className="font-lexend">Admin</span>}
              </NavLink>
            )}
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-4 px-4 py-3 rounded-2xl text-sm font-medium text-gray-500 hover:text-rose-400 hover:bg-rose-400/5 transition-all"
            >
              <LogOut size={20} className="shrink-0" />
              {sidebarOpen && <span className="font-lexend">Sign Out</span>}
            </button>
          </div>
        </div>
      </div>
    </motion.aside>
  )
}
