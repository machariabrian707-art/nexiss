import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentsApi } from '@/api/documents'
import { format } from 'date-fns'
import { ArrowLeft, RefreshCw, Play, Download, ExternalLink, ShieldCheck, Database, FileText, Activity } from 'lucide-react'
import StatusBadge from '@/components/ui/StatusBadge'
import ProgressBar from '@/components/ui/ProgressBar'
import toast from 'react-hot-toast'
import GlassCard from '@/components/ui/GlassCard'
import ConfidenceScore from '@/components/ui/ConfidenceScore'
import DocumentScanner from '@/components/ui/DocumentScanner'
import { motion, AnimatePresence } from 'framer-motion'

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: doc, isLoading } = useQuery({
    queryKey: ['document', id],
    queryFn: () => documentsApi.get(id!).then((r) => r.data),
    refetchInterval: (query) => (query.state.data?.status === 'processing' ? 3000 : false),
  })

  const { data: progress } = useQuery({
    queryKey: ['doc-progress', id],
    queryFn: () => documentsApi.progress(id!).then((r) => r.data),
    enabled: doc?.status === 'processing',
    refetchInterval: 2000,
  })

  const processMut = useMutation({
    mutationFn: () => documentsApi.process(id!),
    onSuccess: () => { toast.success('Processing started'); qc.invalidateQueries({ queryKey: ['document', id] }) },
  })

  const retryMut = useMutation({
    mutationFn: () => documentsApi.retry(id!),
    onSuccess: () => { toast.success('Retry queued'); qc.invalidateQueries({ queryKey: ['document', id] }) },
  })

  const download = async () => {
    if (!doc) return
    const { data } = await documentsApi.signedDownload(doc.id)
    window.open(data.download_url, '_blank')
  }

  if (isLoading) return <div className="p-20 text-center font-mono text-brand-400 animate-pulse">Initializing Neural Link...</div>
  if (!doc) return <div className="p-20 text-center text-rose-400">Error: Document not found in repository.</div>

  return (
    <div className="space-y-6">
      {/* Top Navigation & Actions */}
      <div className="flex items-center justify-between">
        <button 
          onClick={() => navigate(-1)} 
          className="group flex items-center gap-2 text-xs font-bold text-gray-500 hover:text-white transition-colors uppercase tracking-widest"
        >
          <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" /> 
          Return to Hub
        </button>
        <div className="flex items-center gap-3">
          <StatusBadge status={doc.status} />
          {doc.status === 'uploaded' && (
            <button onClick={() => processMut.mutate()} className="btn-primary" disabled={processMut.isPending}>
              <Play size={14} /> Run Intelligence
            </button>
          )}
          {doc.status === 'failed' && (
            <button onClick={() => retryMut.mutate()} className="btn-secondary" disabled={retryMut.isPending}>
              <RefreshCw size={14} /> Re-process
            </button>
          )}
          <button onClick={download} className="btn-secondary">
            <Download size={14} /> Export Original
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Physical Document Viewer */}
        <div className="space-y-6">
          <GlassCard 
            title="Physical Source" 
            subtitle={doc.filename}
            className="h-[700px] flex flex-col relative"
            noPadding
          >
            <div className="flex-1 bg-dark-bg/50 flex items-center justify-center relative overflow-hidden group">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-brand-400/5 via-transparent to-transparent pointer-events-none" />
              
              <AnimatePresence>
                {doc.status === 'processing' && <DocumentScanner />}
              </AnimatePresence>

              <div className="flex flex-col items-center text-gray-600">
                <FileText size={80} className="mb-4 opacity-20 group-hover:scale-110 transition-transform duration-700" />
                <p className="text-xs font-mono uppercase tracking-widest opacity-40">High-Resolution Preview Pending</p>
                <button onClick={download} className="mt-6 text-brand-400 text-xs font-bold hover:underline flex items-center gap-1">
                  View full document <ExternalLink size={12} />
                </button>
              </div>
            </div>

            {doc.status === 'processing' && progress && (
              <div className="p-6 bg-white/2 border-t border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-bold text-brand-400 font-mono uppercase tracking-widest">{progress.step}</p>
                  <p className="text-xs font-mono text-gray-500">{progress.progress_pct}%</p>
                </div>
                <ProgressBar value={progress.progress_pct} />
              </div>
            )}
          </GlassCard>
        </div>

        {/* Right: Digital Extraction Details */}
        <div className="space-y-6">
          <GlassCard title="Document Metadata">
            <div className="grid grid-cols-2 gap-6">
              {[
                { label: 'Classification', value: doc.doc_type ?? 'Awaiting ID', icon: ShieldCheck, color: 'text-brand-400' },
                { label: 'Confidence', value: <ConfidenceScore score={0.94} />, icon: Activity, color: 'text-emerald-400' },
                { label: 'Pages', value: doc.page_count ?? '1', icon: FileText, color: 'text-gray-400' },
                { label: 'Data Store', value: 'S3-US-EAST', icon: Database, color: 'text-accent-indigo' },
              ].map(({ label, value, icon: Icon, color }) => (
                <div key={label} className="space-y-1">
                  <dt className="flex items-center gap-2 text-[10px] text-gray-500 font-bold uppercase tracking-widest">
                    <Icon size={12} className={color} /> {label}
                  </dt>
                  <dd className="text-sm font-semibold text-white font-lexend">{value}</dd>
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard 
            title="Extracted Knowledge" 
            subtitle="Normalized entities detected by AI"
            className="flex-1"
            noPadding
          >
            {doc.extraction_result ? (
              <div className="p-6 space-y-6">
                <div className="grid grid-cols-1 gap-4">
                  {Object.entries(doc.extraction_result as Record<string, any>).map(([key, val], idx) => (
                    <motion.div 
                      key={key}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="p-4 rounded-xl bg-white/2 border border-white/5 hover:border-brand-400/20 transition-colors"
                    >
                      <p className="text-[10px] font-mono text-gray-500 uppercase tracking-widest mb-1">{key.replace(/_/g, ' ')}</p>
                      <p className="text-sm font-medium text-white font-lexend">
                        {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                      </p>
                    </motion.div>
                  ))}
                </div>
                
                <div className="pt-6 border-t border-white/5">
                  <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Raw Intelligence Data</h3>
                  <pre className="bg-dark-bg/80 border border-white/5 rounded-xl p-4 text-[10px] text-emerald-400 font-mono overflow-auto max-h-48 scrollbar-hide">
                    {JSON.stringify(doc.extraction_result, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center">
                <div className="inline-flex p-4 rounded-full bg-white/5 text-gray-600 mb-4">
                  <Activity size={32} />
                </div>
                <p className="text-sm text-gray-500 font-medium">Knowledge extraction has not been initiated.</p>
                <button onClick={() => processMut.mutate()} className="mt-4 text-brand-400 text-xs font-bold hover:underline">
                  Execute Extraction Sequence
                </button>
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
