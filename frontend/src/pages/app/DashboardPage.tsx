import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/api/analytics'
import { documentsApi } from '@/api/documents'
import { FileText, CheckCircle, Clock, AlertCircle, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import StatusBadge from '@/components/ui/StatusBadge'

function StatCard({ label, value, icon: Icon, color }: {
  label: string; value: number | string; icon: React.ElementType; color: string
}) {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: overview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  })

  const { data: recentDocs } = useQuery({
    queryKey: ['documents', 'recent'],
    queryFn: () => documentsApi.list({ limit: 8 }).then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Your document intelligence overview</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Documents" value={overview?.total_documents ?? '—'} icon={FileText} color="bg-brand-500" />
        <StatCard label="Completed" value={overview?.completed ?? '—'} icon={CheckCircle} color="bg-green-500" />
        <StatCard label="Processing" value={overview?.processing ?? '—'} icon={Clock} color="bg-yellow-500" />
        <StatCard label="Failed" value={overview?.failed ?? '—'} icon={AlertCircle} color="bg-red-500" />
      </div>

      {/* Quick actions */}
      <div className="flex gap-3">
        <Link to="/app/upload" className="btn-primary">Upload Document</Link>
        <Link to="/app/documents" className="btn-secondary">View All</Link>
        <Link to="/app/search" className="btn-secondary">Search</Link>
      </div>

      {/* Recent documents */}
      <div className="card">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Recent Documents</h2>
          <Link to="/app/documents" className="text-sm text-brand-600 hover:underline">View all</Link>
        </div>
        <div className="divide-y divide-gray-50">
          {recentDocs?.map((doc) => (
            <Link
              key={doc.id}
              to={`/app/documents/${doc.id}`}
              className="flex items-center justify-between px-5 py-3.5 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <FileText size={16} className="text-gray-400 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                  <p className="text-xs text-gray-400">{doc.doc_type ?? 'Unclassified'}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <StatusBadge status={doc.status} />
                <span className="text-xs text-gray-400">
                  {format(new Date(doc.created_at), 'dd MMM yyyy')}
                </span>
              </div>
            </Link>
          ))}
          {!recentDocs?.length && (
            <div className="px-5 py-10 text-center text-sm text-gray-400">
              No documents yet. <Link to="/app/upload" className="text-brand-600 hover:underline">Upload your first one.</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
