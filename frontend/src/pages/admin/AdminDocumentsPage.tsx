import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '@/api/admin'
import { FileText, RefreshCw } from 'lucide-react'
import { format } from 'date-fns'
import { useState } from 'react'
import StatusBadge from '@/components/ui/StatusBadge'
import toast from 'react-hot-toast'

const STATUS_FILTERS = ['all', 'uploaded', 'processing', 'completed', 'failed']

export default function AdminDocumentsPage() {
  const [page, setPage] = useState(0)
  const [status, setStatus] = useState('all')
  const limit = 25
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'documents', status, page],
    queryFn: () =>
      adminApi.documents({ skip: page * limit, limit, status: status === 'all' ? undefined : status })
        .then((r) => r.data),
  })

  const reprocessMut = useMutation({
    mutationFn: (id: string) => adminApi.reprocessDocument(id),
    onSuccess: () => { toast.success('Reprocess queued'); qc.invalidateQueries({ queryKey: ['admin', 'documents'] }) },
    onError: () => toast.error('Failed to reprocess'),
  })

  const docs: Array<{
    id: string; filename: string; doc_type: string | null;
    status: string; created_at: string; org_name?: string; page_count?: number
  }> = Array.isArray(data) ? data : []

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText size={22} className="text-brand-500" />
          <h1 className="text-2xl font-bold text-gray-900">All Documents</h1>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {STATUS_FILTERS.map((s) => (
          <button
            key={s}
            onClick={() => { setStatus(s); setPage(0) }}
            className={`px-3 py-1.5 rounded-full text-xs font-medium capitalize transition-colors ${
              status === s ? 'bg-gray-800 text-white' : 'bg-white text-gray-600 ring-1 ring-gray-300 hover:bg-gray-50'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b">
              <th className="text-left px-5 py-3 font-medium text-gray-500">Filename</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Type</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Organisation</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Status</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Pages</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Uploaded</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {isLoading && <tr><td colSpan={7} className="px-5 py-10 text-center text-gray-400">Loading...</td></tr>}
            {!isLoading && docs.length === 0 && <tr><td colSpan={7} className="px-5 py-10 text-center text-gray-400">No documents found.</td></tr>}
            {docs.map((doc) => (
              <tr key={doc.id} className="hover:bg-gray-50">
                <td className="px-5 py-3.5 font-medium text-gray-900 max-w-xs truncate">{doc.filename}</td>
                <td className="px-5 py-3.5 text-gray-500">{doc.doc_type ?? '—'}</td>
                <td className="px-5 py-3.5 text-gray-500">{doc.org_name ?? '—'}</td>
                <td className="px-5 py-3.5"><StatusBadge status={doc.status as 'uploaded' | 'processing' | 'completed' | 'failed'} /></td>
                <td className="px-5 py-3.5 text-gray-500">{doc.page_count ?? '—'}</td>
                <td className="px-5 py-3.5 text-gray-400">{format(new Date(doc.created_at), 'dd MMM yyyy')}</td>
                <td className="px-5 py-3.5">
                  <button
                    onClick={() => reprocessMut.mutate(doc.id)}
                    disabled={reprocessMut.isPending}
                    className="flex items-center gap-1 text-xs text-gray-500 hover:text-brand-600"
                  >
                    <RefreshCw size={12} /> Reprocess
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="flex items-center justify-between px-5 py-3 border-t">
          <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0} className="btn-secondary text-xs">Previous</button>
          <span className="text-xs text-gray-500">Page {page + 1}</span>
          <button onClick={() => setPage((p) => p + 1)} disabled={docs.length < limit} className="btn-secondary text-xs">Next</button>
        </div>
      </div>
    </div>
  )
}
