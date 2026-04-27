import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/api/analytics'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar, Legend
} from 'recharts'
import { format, parseISO } from 'date-fns'
import { TrendingUp, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { exportApi } from '@/api/export'
import toast from 'react-hot-toast'

function KPI({ label, value, icon: Icon, color }: {
  label: string; value: string | number; icon: React.ElementType; color: string
}) {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
}

export default function AnalyticsPage() {
  const { data: overview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  })

  const { data: daily } = useQuery({
    queryKey: ['analytics', 'daily'],
    queryFn: () => analyticsApi.dailyProcessing(30).then((r) => r.data),
  })

  const handleExport = async (format: 'csv' | 'xlsx') => {
    try {
      const { data } = await exportApi.exportDocuments(format)
      const url = URL.createObjectURL(data)
      const a = document.createElement('a')
      a.href = url
      a.download = `nexiss-export.${format}`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error('Export failed')
    }
  }

  const chartData = daily?.map((d) => ({
    ...d,
    date: format(parseISO(d.date), 'dd MMM'),
  })) ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-sm text-gray-500 mt-1">Processing trends and document intelligence metrics</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => handleExport('csv')} className="btn-secondary text-sm">Export CSV</button>
          <button onClick={() => handleExport('xlsx')} className="btn-secondary text-sm">Export Excel</button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPI label="Total Documents" value={overview?.total_documents ?? '—'} icon={FileText} color="bg-brand-500" />
        <KPI label="Completed" value={overview?.completed ?? '—'} icon={CheckCircle} color="bg-green-500" />
        <KPI label="Failed" value={overview?.failed ?? '—'} icon={AlertCircle} color="bg-red-500" />
        <KPI label="Total Pages" value={overview?.total_pages ?? '—'} icon={TrendingUp} color="bg-purple-500" />
      </div>

      {/* Area chart — daily docs */}
      <div className="card p-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Documents Processed (Last 30 Days)</h2>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorDocs" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="documents"
              stroke="#2563eb"
              strokeWidth={2}
              fill="url(#colorDocs)"
              name="Documents"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Bar chart — pages */}
      <div className="card p-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Pages Processed (Last 30 Days)</h2>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="pages" fill="#7c3aed" radius={[4, 4, 0, 0]} name="Pages" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
