import { motion } from 'framer-motion'
import { Outlet } from 'react-router-dom'
import Sidebar from '@/components/nav/Sidebar'
import TopBar from '@/components/nav/TopBar'
import { useUIStore } from '@/stores/uiStore'

export default function AppLayout() {
  const sidebarOpen = useUIStore((s) => s.sidebarOpen)

  return (
    <div className="flex h-screen overflow-hidden bg-transparent">
      <Sidebar />
      <div
        className="flex flex-col flex-1 overflow-hidden transition-all duration-300"
        style={{ marginLeft: sidebarOpen ? 256 : 64 }}
      >
        <TopBar />
        <motion.main
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="flex-1 overflow-y-auto p-6"
        >
          <Outlet />
        </motion.main>
      </div>
    </div>
  )
}
