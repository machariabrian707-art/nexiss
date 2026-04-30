import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

// Layouts
import AppLayout from '@/layouts/AppLayout'
import AdminLayout from '@/layouts/AdminLayout'
import AuthLayout from '@/layouts/AuthLayout'

// Auth pages
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'

// User pages
import DashboardPage from '@/pages/app/DashboardPage'
import DocumentsPage from '@/pages/app/DocumentsPage'
import DocumentDetailPage from '@/pages/app/DocumentDetailPage'
import UploadPage from '@/pages/app/UploadPage'
import AnalyticsPage from '@/pages/app/AnalyticsPage'
import SearchPage from '@/pages/app/SearchPage'
import SettingsPage from '@/pages/app/SettingsPage'

// Super admin pages
import AdminDashboardPage from '@/pages/admin/AdminDashboardPage'
import AdminUsersPage from '@/pages/admin/AdminUsersPage'
import AdminOrgsPage from '@/pages/admin/AdminOrgsPage'
import AdminDocumentsPage from '@/pages/admin/AdminDocumentsPage'
import AdminAnalyticsPage from '@/pages/admin/AdminAnalyticsPage'
import AdminBillingPage from '@/pages/admin/AdminBillingPage'
import AdminSystemPage from '@/pages/admin/AdminSystemPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { token, user } = useAuthStore()
  if (!token) return <Navigate to="/login" replace />
  if (!user?.is_superadmin) return <Navigate to="/app" replace />
  return <>{children}</>
}

import { LavaLampBackground } from '@/components/LavaLampBackground'

export default function App() {
  return (
    <>
      <LavaLampBackground />
      <Routes>
        {/* Auth */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* App (org user) */}
      <Route
        path="/app"
        element={
          <PrivateRoute>
            <AppLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="documents/:id" element={<DocumentDetailPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      {/* Super Admin */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminLayout />
          </AdminRoute>
        }
      >
        <Route index element={<AdminDashboardPage />} />
        <Route path="users" element={<AdminUsersPage />} />
        <Route path="orgs" element={<AdminOrgsPage />} />
        <Route path="documents" element={<AdminDocumentsPage />} />
        <Route path="analytics" element={<AdminAnalyticsPage />} />
        <Route path="billing" element={<AdminBillingPage />} />
        <Route path="system" element={<AdminSystemPage />} />
      </Route>

      {/* Default */}
      <Route path="/" element={<Navigate to="/app" replace />} />
      <Route path="*" element={<Navigate to="/app" replace />} />
    </Routes>
  )
}
