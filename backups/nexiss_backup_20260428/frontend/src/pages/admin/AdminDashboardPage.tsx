import { useQuery } from '@tanstack/react-query'
import { adminApi } from '@/api/admin'
import {
  Users, Building2, FileText, AlertCircle,
  Clock, TrendingUp, Activity
} from 'lucide-react'
import { Link } from 'react-router-dom'

function StatCard({ label, value, icon: Icon, color, to }: {
  label: string; value: number | string; icon: React.ElementType; color: string; to?: string
}) {
  const inner = (
    <div className={`card p-5 flex items-center gap-4 hover:shadow-md transition-shadow ${to ? 'cursor-pointer' : ''}`}>
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value ?? '—'}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
  return to ? <Link to={to}>{inner}</Link> : inner
}

export default function AdminDashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: () => adminApi.stats().then((r) => r.data),
    refetchInterval: 30_000,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Super Admin — Platform Overview</h1>
        <p className="text-sm text-gray-500 mt-1">Live view of everything happening on Nexiss</p>
      </div>

      {isLoading && <p className="text-sm text-gray-400">Loading platform stats...</p>}

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard label="Total Organisations" value={stats?.total_orgs ?? 0} icon={Building2} color="bg-brand-500" to="/admin/orgs" />
        <StatCard label="Total Users" value={stats?.total_users ?? 0} icon={Users} color="bg-purple-500" to="/admin/users" />
        <StatCard label="Total Documents" value={stats?.total_documents ?? 0} icon={FileText} color="bg-green-500" to="/admin/documents" />
        <StatCard label="Documents Today" value={stats?.documents_today ?? 0} icon={TrendingUp} color="bg-blue-500" />
        <StatCard label="Failed Documents" value={stats?.failed_documents ?? 0} icon={AlertCircle} color="bg-red-500" to="/admin/documents" />
        <StatCard label="Processing Queue" value={stats?.processing_queue ?? 0} icon={Clock} color="bg-yellow-500" />
      </div>

      {/* System health indicators */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity size={16} className="text-green-500" />
          <h2 className="font-semibold text-gray-800">System Status</h2>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'API', status: 'Operational' },
            { label: 'OCR Pipeline', status: 'Operational' },
            { label: 'Storage (S3)', status: 'Operational' },
            { label: 'Queue (Redis)', status: 'Operational' },
            { label: 'Database', status: 'Operational' },
            { label: 'AI Extraction', status: 'Operational' },
          ].map(({ label, status }) => (
            <div key={label} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <span className="w-2 h-2 rounded-full bg-green-400 shrink-0" />
              <div>
                <p className="text-xs font-medium text-gray-700">{label}</p>
                <p className="text-xs text-gray-400">{status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick links */}
      <div className="flex gap-3">
        <Link to="/admin/documents" className="btn-secondary text-sm">View All Documents</Link>
        <Link to="/admin/users" className="btn-secondary text-sm">Manage Users</Link>
        <Link to="/admin/analytics" className="btn-secondary text-sm">Analytics</Link>
        <Link to="/admin/system" className="btn-secondary text-sm">System Logs</Link>
      </div>
    </div>
  )
}
