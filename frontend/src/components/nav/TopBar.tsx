import { Bell, ChevronDown, Search, Activity } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { motionTokens } from '@/lib/motion'

interface TopBarProps { isAdmin?: boolean }

export default function TopBar({ isAdmin }: TopBarProps) {
  const { user, orgs, activeOrgId, setActiveOrg } = useAuthStore()
  const [orgOpen, setOrgOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  const activeOrg = orgs.find((o) => o.id === activeOrgId)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    onScroll()
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{
        opacity: scrolled ? 0.95 : 1,
        y: 0,
        backdropFilter: `blur(${scrolled ? 12 : 0}px)`,
      }}
      transition={{ duration: motionTokens.duration.base, ease: motionTokens.ease.entrance }}
      className="h-20 flex items-center justify-between px-8 bg-dark-bg/60 border-b border-white/5 sticky top-0 z-30"
      style={{ willChange: 'transform, opacity' }}
    >
      {/* Left: Organization Context */}
      <div className="flex items-center gap-8">
        <div className="relative">
          {!isAdmin && orgs.length > 0 && (
            <button
              onClick={() => setOrgOpen((o) => !o)}
              className="group relative flex items-center gap-3 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-sm font-medium text-gray-200 hover:bg-white/10 transition-all shadow-inner"
            >
              <div className="w-2 h-2 rounded-full bg-brand-400 animate-pulse shadow-glow-brand" />
              <span>{activeOrg?.name ?? 'Select Context'}</span>
              <ChevronDown size={14} className="text-gray-500" />
              <span className="pointer-events-none absolute left-4 right-4 bottom-1 h-px origin-left scale-x-0 bg-brand-400 transition-transform duration-200 group-hover:scale-x-100" />
            </button>
          )}
          {isAdmin && (
            <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-accent-indigo/10 border border-accent-indigo/20">
              <Activity size={16} className="text-accent-indigo" />
              <span className="text-xs font-bold text-accent-indigo uppercase tracking-widest">Platform Admin</span>
            </div>
          )}
          {orgOpen && (
            <div className="absolute top-12 left-0 z-50 w-64 glass rounded-2xl py-2 shadow-2xl border-white/10 overflow-hidden">
              {orgs.map((org) => (
                <button
                  key={org.id}
                  onClick={() => { setActiveOrg(org.id); setOrgOpen(false) }}
                  className={`w-full text-left px-4 py-3 text-sm transition-colors hover:bg-white/5 ${
                    org.id === activeOrgId ? 'text-brand-400 font-bold bg-white/5' : 'text-gray-400'
                  }`}
                >
                  {org.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Command Center Trigger (Visual only for now) */}
        {!isAdmin && (
          <div className="group relative hidden md:flex items-center gap-3 px-4 py-2 w-80 rounded-xl bg-white/5 border border-white/10 text-gray-500 cursor-text hover:bg-white/10 transition-all">
            <Search size={16} />
            <span className="text-sm">Search documents...</span>
            <span className="ml-auto text-[10px] bg-white/10 px-1.5 py-0.5 rounded border border-white/10 font-mono">⌘K</span>
            <span className="pointer-events-none absolute left-4 right-4 bottom-1 h-px origin-left scale-x-0 bg-brand-400 transition-transform duration-200 group-hover:scale-x-100" />
          </div>
        )}
      </div>

      {/* Right: Telemetry + User */}
      <div className="flex items-center gap-6">
        <div className="hidden lg:flex items-center gap-6 text-[10px] font-mono text-gray-500 uppercase tracking-widest border-r border-white/10 pr-6">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            System: Nominal
          </div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
            AI: Ready
          </div>
        </div>

        <button className="relative p-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all">
          <Bell size={20} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-dark-bg" />
        </button>

        <div className="flex items-center gap-3 pl-2">
          <div className="flex flex-col items-end hidden sm:flex">
            <span className="text-sm font-bold text-white font-lexend">{user?.full_name}</span>
            <span className="text-[10px] text-gray-500 font-mono uppercase tracking-tighter">
              {isAdmin ? 'Platform Access' : (user?.active_org_role ?? 'member').replace('_', ' ')}
            </span>
          </div>
          <div className="relative group">
            <div className="absolute inset-0 bg-brand-400 blur-md opacity-20 group-hover:opacity-40 transition-opacity" />
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-accent-indigo flex items-center justify-center text-white text-sm font-bold shadow-glow-brand">
              {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  )
}
