import { useState } from 'react'
import { searchApi } from '@/api/search'
import { Search, FileText } from 'lucide-react'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import StatusBadge from '@/components/ui/StatusBadge'
import toast from 'react-hot-toast'

const DOC_TYPE_FILTERS = ['All Types', 'Invoice', 'Receipt', 'Patient Record', 'Contract', 'Lab Result', 'Prescription', 'Bank Statement', 'Other']

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [docType, setDocType] = useState('All Types')
  const [results, setResults] = useState<unknown[]>([])
  const [searched, setSearched] = useState(false)
  const [loading, setLoading] = useState(false)

  const doSearch = async (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    try {
      const { data } = await searchApi.search(query, {
        doc_type: docType === 'All Types' ? undefined : docType,
      })
      setResults(data as unknown[])
      setSearched(true)
    } catch {
      toast.error('Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Search</h1>
        <p className="text-sm text-gray-500 mt-1">
          Find documents by content, entity, patient name, invoice number, and more.
        </p>
      </div>

      <form onSubmit={doSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            className="input pl-9"
            placeholder='e.g. "Doshi" or "Invoice 1042" or "John patient record"'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
          className="input w-40"
        >
          {DOC_TYPE_FILTERS.map((t) => <option key={t}>{t}</option>)}
        </select>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {/* Results */}
      {searched && (
        <div className="card divide-y divide-gray-50">
          {results.length === 0 && (
            <div className="px-5 py-10 text-center text-sm text-gray-400">
              No results found for <strong>"{query}"</strong>.
            </div>
          )}
          {(results as Array<{
            id: string; filename: string; doc_type: string;
            status: string; created_at: string; snippet?: string
          }>).map((doc) => (
            <Link
              key={doc.id}
              to={`/app/documents/${doc.id}`}
              className="flex items-start gap-3 px-5 py-4 hover:bg-gray-50 transition-colors"
            >
              <FileText size={18} className="text-gray-400 mt-0.5 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                <p className="text-xs text-gray-400 mt-0.5">{doc.doc_type ?? 'Unclassified'} · {format(new Date(doc.created_at), 'dd MMM yyyy')}</p>
                {doc.snippet && (
                  <p className="text-xs text-gray-500 mt-1 italic">...{doc.snippet}...</p>
                )}
              </div>
              <StatusBadge status={doc.status as 'uploaded' | 'processing' | 'completed' | 'failed'} />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
