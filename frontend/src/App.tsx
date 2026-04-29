import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'

import AuthLayout from '@/layouts/AuthLayout'
import AppLayout from '@/layouts/AppLayout'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import DashboardPage from '@/pages/app/DashboardPage'
import DocumentsPage from '@/pages/app/DocumentsPage'
import SearchPage from '@/pages/app/SearchPage'
import AnalyticsPage from '@/pages/app/AnalyticsPage'
import AdminPage from '@/pages/admin/AdminDashboardPage'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
})

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

function RequireAdmin({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />
  if (!user.is_superuser) return <Navigate to="/app" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Toaster position="top-right" />
        <Routes>
          {/* Auth routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          {/* App routes */}
          <Route
            path="/app"
            element={
              <RequireAuth>
                <AppLayout />
              </RequireAuth>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
          </Route>

          {/* Super admin */}
          <Route
            path="/admin"
            element={
              <RequireAdmin>
                <AppLayout />
              </RequireAdmin>
            }
          >
            <Route index element={<AdminPage />} />
          </Route>

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/app" replace />} />
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
