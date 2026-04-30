import { Outlet } from 'react-router-dom'
import AdminSidebar from '@/components/nav/AdminSidebar'
import TopBar from '@/components/nav/TopBar'
import { useUIStore } from '@/stores/uiStore'

export default function AdminLayout() {
  const sidebarOpen = useUIStore((s) => s.sidebarOpen)

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <AdminSidebar />
      <div
        className="flex flex-col flex-1 overflow-hidden transition-all duration-300"
        style={{ marginLeft: sidebarOpen ? 256 : 64 }}
      >
        <TopBar isAdmin />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
