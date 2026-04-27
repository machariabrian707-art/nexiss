import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentsApi } from '@/api/documents'
import { format } from 'date-fns'
import { ArrowLeft, RefreshCw, Play, Download } from 'lucide-react'
import StatusBadge from '@/components/ui/StatusBadge'
import ProgressBar from '@/components/ui/ProgressBar'
import toast from 'react-hot-toast'

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: doc, isLoading } = useQuery({
    queryKey: ['document', id],
    queryFn: () => documentsApi.get(id!).then((r) => r.data),
    refetchInterval: (d) => (d?.status === 'processing' ? 3000 : false),
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

  if (isLoading) return <div className="p-10 text-center text-gray-400">Loading...</div>
  if (!doc) return <div className="p-10 text-center text-red-400">Document not found.</div>

  return (
    <div className="max-w-4xl space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800">
        <ArrowLeft size={16} /> Back
      </button>

      <div className="card p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">{doc.filename}</h1>
            <p className="text-sm text-gray-400 mt-1">{format(new Date(doc.created_at), 'dd MMM yyyy, HH:mm')}</p>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={doc.status} />
            {doc.status === 'uploaded' && (
              <button onClick={() => processMut.mutate()} className="btn-primary" disabled={processMut.isPending}>
                <Play size={14} /> Process
              </button>
            )}
            {doc.status === 'failed' && (
              <button onClick={() => retryMut.mutate()} className="btn-secondary" disabled={retryMut.isPending}>
                <RefreshCw size={14} /> Retry
              </button>
            )}
            <button onClick={download} className="btn-secondary">
              <Download size={14} /> Download
            </button>
          </div>
        </div>

        <dl className="mt-6 grid grid-cols-3 gap-4">
          {[
            { label: 'Document Type', value: doc.doc_type ?? 'Unclassified' },
            { label: 'Pages', value: doc.page_count ?? '—' },
            { label: 'Organisation', value: doc.org_id.slice(0, 8) + '...' },
          ].map(({ label, value }) => (
            <div key={label} className="bg-gray-50 rounded-lg p-4">
              <dt className="text-xs text-gray-500 font-medium">{label}</dt>
              <dd className="mt-1 text-sm font-semibold text-gray-900">{value}</dd>
            </div>
          ))}
        </dl>

        {/* Processing progress */}
        {doc.status === 'processing' && progress && (
          <div className="mt-6">
            <p className="text-sm font-medium text-gray-700 mb-2">{progress.step}</p>
            <ProgressBar value={progress.progress_pct} />
          </div>
        )}

        {/* Extraction result */}
        {doc.extraction_result && (
          <div className="mt-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Extracted Data</h2>
            <pre className="bg-gray-900 text-green-300 rounded-xl p-4 text-xs overflow-auto max-h-96">
              {JSON.stringify(doc.extraction_result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
