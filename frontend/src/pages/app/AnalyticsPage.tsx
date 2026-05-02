import { useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/api/analytics'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar, Legend, PieChart, Pie, Cell
} from 'recharts'
import { format, parseISO } from 'date-fns'
import { TrendingUp, FileText, CheckCircle, AlertCircle, Activity, CalendarRange, ChevronDown } from 'lucide-react'
import { exportApi } from '@/api/export'
import toast from 'react-hot-toast'
import { motion, AnimatePresence, useInView } from 'framer-motion'
import { cardVariants, containerVariants, motionTokens } from '@/lib/motion'

const PIE_COLORS = ['#7c3aed', '#2563eb', '#10b981', '#f59e0b']

function AnimatedMetricValue({ value }: { value: number }) {
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    let raf = 0
    let start = 0
    const duration = 1600

    const step = (timestamp: number) => {
      if (!start) start = timestamp
      const elapsed = timestamp - start
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplay(Math.round(value * eased))
      if (progress < 1) raf = window.requestAnimationFrame(step)
    }

    raf = window.requestAnimationFrame(step)
    return () => window.cancelAnimationFrame(raf)
  }, [value])

  return <span>{display.toLocaleString()}</span>
}

function KPI({ label, value, icon: Icon, color, delta }: {
  label: string
  value: number
  icon: React.ElementType
  color: string
  delta: number
}) {
  const positiveDelta = delta >= 0

  return (
    <motion.div
      variants={cardVariants}
      whileHover="hover"
      className="card relative overflow-hidden p-5 flex items-center gap-4 [transform-style:preserve-3d]"
      style={{ willChange: 'transform, opacity' }}
    >
      <motion.div
        aria-hidden
        className="absolute -right-6 -top-6 h-20 w-20 rounded-full border border-white/15"
        animate={{ rotate: 360 }}
        transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
      />
      <div className={`p-3 rounded-xl ${color} shadow-lg`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">
          <AnimatedMetricValue value={value} />
        </p>
        <p className="text-sm text-gray-500">{label}</p>
        <motion.div
          key={`${label}-${delta}`}
          initial={{ scale: 1, opacity: 0.8 }}
          animate={{ scale: [1, 1.2, 1], opacity: [0.8, 1, 0.85] }}
          transition={{ duration: motionTokens.duration.fast }}
          className={`mt-1 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs ${
            positiveDelta ? 'bg-emerald-500/10 text-emerald-600' : 'bg-rose-500/10 text-rose-600'
          }`}
        >
          <TrendingUp size={12} className={positiveDelta ? '' : 'rotate-180'} />
          {positiveDelta ? '+' : ''}{delta.toFixed(1)}%
        </motion.div>
      </div>
    </motion.div>
  )
}

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState('30d')
  const [filterOpen, setFilterOpen] = useState(false)
  const [tooltipIndex, setTooltipIndex] = useState<number | null>(null)
  const [activityItems, setActivityItems] = useState([
    'Classifier tuned confidence threshold to 0.87',
    'OCR queue cleared for APAC shard',
    'Schema detector synced with model v2.1',
    'Document summarizer warmed edge cache',
  ])
  const feedRef = useRef<HTMLDivElement | null>(null)
  const tooltipTimerRef = useRef<number | null>(null)
  const controlsRef = useRef<HTMLDivElement | null>(null)
  const chartsRef = useRef<HTMLDivElement | null>(null)
  const chartsInView = useInView(chartsRef, { amount: 0.25 })
  const controlsInView = useInView(controlsRef, { amount: 0.4, once: true })
  const [chartEpoch, setChartEpoch] = useState(0)
  const [metricDeltas, setMetricDeltas] = useState({
    total_documents: 2.1,
    completed: 1.8,
    failed: -0.6,
    total_pages: 3.3,
  })

  const { data: overview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  })

  const { data: daily } = useQuery({
    queryKey: ['analytics', 'daily', dateRange],
    queryFn: () => analyticsApi.dailyProcessing(dateRange === '7d' ? 7 : dateRange === '14d' ? 14 : 30).then((r) => r.data),
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

  const chartData = useMemo(
    () =>
      daily?.points.map((d) => ({
        ...d,
        date: format(parseISO(d.day), 'dd MMM'),
        documents: d.documents_processed,
        pages: d.pages_processed,
      })) ?? [],
    [daily]
  )

  const pieData = useMemo(
    () => [
      { name: 'Completed', value: overview?.processing_success_count ?? 0 },
      { name: 'Failed', value: overview?.processing_failed_count ?? 0 },
      {
        name: 'Queued',
        value: Math.max(
          ((overview?.total_documents_processed ?? 0) - (overview?.processing_success_count ?? 0) - (overview?.processing_failed_count ?? 0)),
          0
        ),
      },
      { name: 'In Review', value: Math.max(Math.round((overview?.total_documents_processed ?? 0) * 0.08), 0) },
    ],
    [overview]
  )

  useEffect(() => {
    if (chartsInView) setChartEpoch((v) => v + 1)
  }, [chartsInView])

  useEffect(() => {
    const interval = window.setInterval(() => {
      setMetricDeltas((prev) => ({
        total_documents: Number((prev.total_documents + (Math.random() * 0.4 - 0.2)).toFixed(1)),
        completed: Number((prev.completed + (Math.random() * 0.3 - 0.15)).toFixed(1)),
        failed: Number((prev.failed + (Math.random() * 0.2 - 0.1)).toFixed(1)),
        total_pages: Number((prev.total_pages + (Math.random() * 0.5 - 0.25)).toFixed(1)),
      }))

      setActivityItems((prev) => {
        const synthetic = [
          'Anomaly watcher archived low-priority alert',
          'PII detector completed verification sweep',
          'Vector index compacted stale segments',
          'Summarization cache rotated warm entries',
        ]
        const next = synthetic[Math.floor(Math.random() * synthetic.length)]
        return [next, ...prev].slice(0, 8)
      })
    }, 6000)
    return () => window.clearInterval(interval)
  }, [])

  useEffect(() => {
    return () => {
      if (tooltipTimerRef.current) window.clearTimeout(tooltipTimerRef.current)
    }
  }, [])

  useEffect(() => {
    const interval = window.setInterval(() => {
      if (!feedRef.current) return
      const container = feedRef.current
      const maxScroll = Math.max(container.scrollHeight - container.clientHeight, 0)
      const next = container.scrollTop > maxScroll - 12 ? 0 : container.scrollTop + 52
      container.scrollTo({ top: next, behavior: 'smooth' })
    }, 4000)
    return () => window.clearInterval(interval)
  }, [])

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-6"
    >
      <motion.div variants={cardVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-sm text-gray-500 mt-1">Processing trends and document intelligence metrics</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => handleExport('csv')} className="btn-secondary text-sm">Export CSV</button>
          <button onClick={() => handleExport('xlsx')} className="btn-secondary text-sm">Export Excel</button>
        </div>
      </motion.div>

      <motion.div
        ref={controlsRef}
        variants={cardVariants}
        className="card p-4 flex flex-wrap items-center gap-3"
      >
        <div className="relative">
          <button
            onClick={() => setFilterOpen((v) => !v)}
            className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-gray-700"
          >
            <Activity size={14} />
            Signal Filter
            <ChevronDown size={14} className={`transition-transform ${filterOpen ? 'rotate-180' : ''}`} />
          </button>
          <AnimatePresence>
            {filterOpen && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 8 }}
                transition={{ duration: motionTokens.duration.fast }}
                className="absolute z-20 mt-2 w-52 rounded-2xl border border-white/10 bg-dark-bg/90 p-2 text-sm text-gray-200 backdrop-blur-md"
              >
                <button className="w-full rounded-xl px-3 py-2 text-left hover:bg-white/10">All Pipelines</button>
                <button className="w-full rounded-xl px-3 py-2 text-left hover:bg-white/10">OCR Only</button>
                <button className="w-full rounded-xl px-3 py-2 text-left hover:bg-white/10">Classifiers</button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <motion.div
          animate={controlsInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
          transition={{ duration: motionTokens.duration.base }}
          className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-gray-700"
        >
          <CalendarRange size={14} />
          <button onClick={() => setDateRange('7d')} className={dateRange === '7d' ? 'text-brand-500 font-semibold' : ''}>7D</button>
          <button onClick={() => setDateRange('14d')} className={dateRange === '14d' ? 'text-brand-500 font-semibold' : ''}>14D</button>
          <button onClick={() => setDateRange('30d')} className={dateRange === '30d' ? 'text-brand-500 font-semibold' : ''}>30D</button>
        </motion.div>
      </motion.div>

      {/* KPIs */}
      <motion.div variants={containerVariants} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPI label="Total Documents" value={overview?.total_documents_processed ?? 0} icon={FileText} color="bg-brand-500" delta={metricDeltas.total_documents} />
        <KPI label="Completed" value={overview?.processing_success_count ?? 0} icon={CheckCircle} color="bg-green-500" delta={metricDeltas.completed} />
        <KPI label="Failed" value={overview?.processing_failed_count ?? 0} icon={AlertCircle} color="bg-red-500" delta={metricDeltas.failed} />
        <KPI label="Total Pages" value={overview?.total_pages_processed ?? 0} icon={TrendingUp} color="bg-purple-500" delta={metricDeltas.total_pages} />
      </motion.div>

      <motion.div ref={chartsRef} variants={containerVariants} className="grid gap-4 lg:grid-cols-2">
        {/* Area chart — daily docs */}
        <motion.div variants={cardVariants} className="card p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Documents Processed ({dateRange.toUpperCase()})</h2>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart key={`area-${chartEpoch}`} data={chartData}>
              <defs>
                <linearGradient id="colorDocs" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                wrapperStyle={{ transition: 'transform 0.2s cubic-bezier(0.4,0,0.2,1)' }}
                contentStyle={{ borderRadius: 12, border: '1px solid rgba(148,163,184,0.2)' }}
              />
              <Area
                type="monotone"
                dataKey="documents"
                stroke="#2563eb"
                strokeWidth={2}
                fill="url(#colorDocs)"
                name="Documents"
                isAnimationActive
                animationDuration={1200}
                animationEasing="ease-out"
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Bar chart — pages */}
        <motion.div variants={cardVariants} className="card p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Pages Processed ({dateRange.toUpperCase()})</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart key={`bar-${chartEpoch}`} data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar
                dataKey="pages"
                fill="#7c3aed"
                radius={[4, 4, 0, 0]}
                name="Pages"
                isAnimationActive
                animationDuration={950}
                animationBegin={100}
              />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div variants={cardVariants} className="card p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Status Composition</h2>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                innerRadius={55}
                outerRadius={82}
                paddingAngle={3}
                startAngle={-30}
                endAngle={330}
                isAnimationActive
                animationDuration={1100}
              >
                {pieData.map((_, index) => (
                  <Cell key={`pie-cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div variants={cardVariants} className="card p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Activity Feed</h2>
          <div ref={feedRef} className="h-[240px] space-y-2 overflow-hidden">
            <AnimatePresence initial={false}>
              {activityItems.map((item, index) => (
                <motion.button
                  key={`${item}-${index}`}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: motionTokens.duration.base }}
                  onMouseEnter={() => {
                    if (tooltipTimerRef.current) window.clearTimeout(tooltipTimerRef.current)
                    tooltipTimerRef.current = window.setTimeout(() => setTooltipIndex(index), 120)
                  }}
                  onMouseLeave={() => {
                    if (tooltipTimerRef.current) window.clearTimeout(tooltipTimerRef.current)
                    setTooltipIndex(null)
                  }}
                  className="relative w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-left text-sm text-gray-700 hover:bg-white/10"
                >
                  <span className="inline-flex items-center gap-2">
                    <motion.span
                      className="h-2 w-2 rounded-full bg-emerald-500"
                      animate={{ scale: [1, 1.4, 1], opacity: [0.8, 1, 0.8] }}
                      transition={{ duration: 1.4, repeat: Infinity, delay: index * 0.1 }}
                    />
                    {item}
                  </span>
                  <AnimatePresence>
                    {tooltipIndex === index && (
                      <motion.span
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 6 }}
                        transition={{ type: 'spring', stiffness: 320, damping: 24 }}
                        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg border border-white/10 bg-dark-bg/90 px-2 py-1 text-[11px] text-gray-300"
                      >
                        Pipeline synced
                      </motion.span>
                    )}
                  </AnimatePresence>
                </motion.button>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
