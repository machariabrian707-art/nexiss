import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/api/analytics'
import { documentsApi } from '@/api/documents'
import { FileText, CheckCircle, Clock, AlertCircle, TrendingUp, Zap, ArrowRight, Activity } from 'lucide-react'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import StatusBadge from '@/components/ui/StatusBadge'
import GlassCard from '@/components/ui/GlassCard'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts'
import { motion } from 'framer-motion'

function StatCard({ label, value, icon: Icon, color, trend }: {
  label: string; value: number | string; icon: React.ElementType; color: string; trend?: string
}) {
  return (
    <GlassCard className="relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] font-mono font-bold text-gray-500 uppercase tracking-widest">{label}</p>
          <p className="text-3xl font-bold text-white mt-1 font-lexend">{value}</p>
          {trend && (
            <div className="flex items-center gap-1 mt-2 text-[10px] font-bold text-emerald-400">
              <TrendingUp size={12} />
              <span>{trend}</span>
            </div>
          )}
        </div>
        <div className={clsx('p-3 rounded-2xl bg-white/5 border border-white/10', color)}>
          <Icon size={20} className="text-white" />
        </div>
      </div>
      {/* Decorative background glow */}
      <div className={clsx('absolute -bottom-6 -right-6 w-24 h-24 blur-3xl opacity-10 rounded-full', color)} />
    </GlassCard>
  )
}

import clsx from 'clsx'

export default function DashboardPage() {
  const { data: overview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  })

  const { data: recentDocs } = useQuery({
    queryKey: ['documents', 'recent'],
    queryFn: () => documentsApi.list({ limit: 5 }).then((r) => r.data),
  })

  const { data: dailyStats } = useQuery({
    queryKey: ['analytics', 'daily'],
    queryFn: () => analyticsApi.dailyProcessing(14).then((r) => r.data),
  })

  const chartData = dailyStats?.map(d => ({
    name: format(new Date(d.date), 'MMM dd'),
    count: d.count
  })) ?? []

  return (
    <div className="space-y-8 pb-12">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2 text-brand-400 mb-2"
          >
            <Activity size={16} />
            <span className="text-[10px] font-mono font-bold uppercase tracking-widest">Neural Network Active</span>
          </motion.div>
          <h1 className="text-4xl font-bold text-white font-lexend tracking-tight">Intelligence Hub</h1>
          <p className="text-gray-500 mt-1 max-w-md">Real-time document classification and entity extraction monitoring.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/app/upload" className="btn-primary">
            <Zap size={16} /> Ingest Data
          </Link>
          <Link to="/app/search" className="btn-secondary">
            Discovery
          </Link>
        </div>
      </div>

      {/* Bento Grid Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Inflow" value={overview?.total_documents ?? '0'} icon={FileText} color="text-brand-400" trend="+12% today" />
        <StatCard label="Extracted" value={overview?.completed ?? '0'} icon={CheckCircle} color="text-emerald-400" trend="98.2% Accuracy" />
        <StatCard label="In-Flight" value={overview?.processing ?? '0'} icon={Clock} color="text-amber-400" />
        <StatCard label="Anomalies" value={overview?.failed ?? '0'} icon={AlertCircle} color="text-rose-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart Card */}
        <GlassCard 
          title="Throughput Velocity" 
          subtitle="Processed documents over the last 14 cycles"
          className="lg:col-span-2"
        >
          <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="name" 
                  stroke="#4b5563" 
                  fontSize={10} 
                  tickLine={false} 
                  axisLine={false} 
                  dy={10}
                />
                <YAxis hide />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#0F172A', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    fontSize: '12px'
                  }}
                  itemStyle={{ color: '#38bdf8' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#38bdf8" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorCount)" 
                  animationDuration={2000}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Recent Activity Ticker */}
        <GlassCard 
          title="Live Repository Feed" 
          subtitle="Recent ingestions"
          noPadding
        >
          <div className="divide-y divide-white/5">
            {recentDocs?.map((doc, idx) => (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                key={doc.id}
              >
                <Link
                  to={`/app/documents/${doc.id}`}
                  className="flex items-center justify-between px-6 py-4 hover:bg-white/5 transition-colors group"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-2 rounded-lg bg-white/5 text-gray-400 group-hover:text-brand-400 transition-colors">
                      <FileText size={16} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white truncate max-w-[120px]">{doc.filename}</p>
                      <p className="text-[10px] text-gray-500 font-mono uppercase">{doc.doc_type?.replace('_', ' ') ?? 'Unclassified'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <StatusBadge status={doc.status} />
                    <ArrowRight size={14} className="text-gray-600 opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0" />
                  </div>
                </Link>
              </motion.div>
            ))}
            {!recentDocs?.length && (
              <div className="px-6 py-12 text-center">
                <p className="text-sm text-gray-500">No active telemetry found.</p>
                <Link to="/app/upload" className="text-brand-400 text-xs mt-2 inline-block hover:underline">Start Ingestion</Link>
              </div>
            )}
          </div>
          <div className="p-4 border-t border-white/5">
            <Link to="/app/documents" className="flex items-center justify-center gap-2 text-xs font-bold text-gray-400 hover:text-white transition-colors">
              Access Full Repository <ArrowRight size={12} />
            </Link>
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
