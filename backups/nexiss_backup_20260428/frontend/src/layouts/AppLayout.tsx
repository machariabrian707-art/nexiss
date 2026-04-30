import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from '@/components/nav/Sidebar'
import TopBar from '@/components/nav/TopBar'
import { motion, AnimatePresence } from 'framer-motion'

export default function AppLayout() {
  const location = useLocation()

  return (
    <div className="flex h-screen overflow-hidden bg-dark-bg text-gray-200">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden transition-all duration-300">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-4 lg:p-8 scrollbar-hide">
          <div className="max-w-7xl mx-auto">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  )
}
