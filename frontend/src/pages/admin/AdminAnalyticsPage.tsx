import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/api/analytics'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts'
import { format, parseISO } from 'date-fns'
import { adminApi } from '@/api/admin'

export default function AdminAnalyticsPage() {
  const { data: stats } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: () => adminApi.stats().then((r) => r.data),
  })

  const { data: daily } = useQuery({
    queryKey: ['analytics', 'daily', 60],
    queryFn: () => analyticsApi.dailyProcessing(60).then((r) => r.data),
  })

  const chartData = daily?.map((d) => ({
    ...d,
    date: format(parseISO(d.date), 'dd MMM'),
  })) ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Platform Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">Global document processing metrics across all organisations</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Total Documents', value: stats?.total_documents },
          { label: 'Documents Today', value: stats?.documents_today },
          { label: 'Failed', value: stats?.failed_documents },
        ].map(({ label, value }) => (
          <div key={label} className="card p-5">
            <p className="text-2xl font-bold text-gray-900">{value ?? '—'}</p>
            <p className="text-sm text-gray-500">{label}</p>
          </div>
        ))}
      </div>

      <div className="card p-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Documents Processed (Last 60 Days)</h2>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Area type="monotone" dataKey="documents" stroke="#7c3aed" strokeWidth={2} fill="url(#grad)" name="Documents" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="card p-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Pages Processed</h2>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="pages" fill="#2563eb" radius={[4, 4, 0, 0]} name="Pages" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
