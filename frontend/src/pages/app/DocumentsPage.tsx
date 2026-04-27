import { useQuery } from '@tanstack/react-query'
import { documentsApi } from '@/api/documents'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { FileText, RefreshCw } from 'lucide-react'
import { format } from 'date-fns'
import StatusBadge from '@/components/ui/StatusBadge'

const STATUS_FILTERS = ['all', 'uploaded', 'processing', 'completed', 'failed']

export default function DocumentsPage() {
  const [status, setStatus] = useState('all')
  const [page, setPage] = useState(0)
  const limit = 20

  const { data: docs, isLoading, refetch } = useQuery({
    queryKey: ['documents', status, page],
    queryFn: () =>
      documentsApi.list({
        status: status === 'all' ? undefined : status,
        skip: page * limit,
        limit,
      }).then((r) => r.data),
  })

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-sm text-gray-500 mt-1">All documents in your organisation</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="btn-secondary">
            <RefreshCw size={15} /> Refresh
          </button>
          <Link to="/app/upload" className="btn-primary">Upload</Link>
        </div>
      </div>

      {/* Status filter */}
      <div className="flex gap-2 flex-wrap">
        {STATUS_FILTERS.map((s) => (
          <button
            key={s}
            onClick={() => { setStatus(s); setPage(0) }}
            className={`px-3 py-1.5 rounded-full text-xs font-medium capitalize transition-colors ${
              status === s
                ? 'bg-brand-500 text-white'
                : 'bg-white text-gray-600 ring-1 ring-gray-300 hover:bg-gray-50'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              <th className="text-left px-5 py-3 font-medium text-gray-500">Filename</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Type</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Status</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Pages</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Uploaded</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {isLoading && (
              <tr><td colSpan={5} className="px-5 py-10 text-center text-gray-400">Loading...</td></tr>
            )}
            {!isLoading && !docs?.length && (
              <tr><td colSpan={5} className="px-5 py-10 text-center text-gray-400">No documents found.</td></tr>
            )}
            {docs?.map((doc) => (
              <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-5 py-3.5">
                  <Link to={`/app/documents/${doc.id}`} className="flex items-center gap-2 text-brand-600 font-medium hover:underline">
                    <FileText size={14} className="text-gray-400" />
                    {doc.filename}
                  </Link>
                </td>
                <td className="px-5 py-3.5 text-gray-600">{doc.doc_type ?? <span className="text-gray-300">—</span>}</td>
                <td className="px-5 py-3.5"><StatusBadge status={doc.status} /></td>
                <td className="px-5 py-3.5 text-gray-600">{doc.page_count ?? '—'}</td>
                <td className="px-5 py-3.5 text-gray-400">{format(new Date(doc.created_at), 'dd MMM yyyy')}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-gray-100">
          <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0} className="btn-secondary text-xs">
            Previous
          </button>
          <span className="text-xs text-gray-500">Page {page + 1}</span>
          <button onClick={() => setPage((p) => p + 1)} disabled={(docs?.length ?? 0) < limit} className="btn-secondary text-xs">
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
