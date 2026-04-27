import { useQuery } from '@tanstack/react-query'
import { adminApi } from '@/api/admin'
import { Building2, Users } from 'lucide-react'
import { format } from 'date-fns'
import { useState } from 'react'

export default function AdminOrgsPage() {
  const [page, setPage] = useState(0)
  const limit = 20

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'orgs', page],
    queryFn: () => adminApi.orgs({ skip: page * limit, limit }).then((r) => r.data),
  })

  const orgs: Array<{
    id: string; name: string; slug: string;
    created_at: string; member_count?: number; document_count?: number
  }> = Array.isArray(data) ? data : []

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2">
        <Building2 size={22} className="text-brand-500" />
        <h1 className="text-2xl font-bold text-gray-900">Organisations</h1>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b">
              <th className="text-left px-5 py-3 font-medium text-gray-500">Name</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Slug</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Members</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Documents</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {isLoading && <tr><td colSpan={5} className="px-5 py-10 text-center text-gray-400">Loading...</td></tr>}
            {!isLoading && orgs.length === 0 && <tr><td colSpan={5} className="px-5 py-10 text-center text-gray-400">No organisations yet.</td></tr>}
            {orgs.map((org) => (
              <tr key={org.id} className="hover:bg-gray-50">
                <td className="px-5 py-3.5 font-medium text-gray-900">{org.name}</td>
                <td className="px-5 py-3.5 text-gray-500 font-mono text-xs">{org.slug}</td>
                <td className="px-5 py-3.5 text-gray-600">
                  <span className="flex items-center gap-1"><Users size={12} />{org.member_count ?? '—'}</span>
                </td>
                <td className="px-5 py-3.5 text-gray-600">{org.document_count ?? '—'}</td>
                <td className="px-5 py-3.5 text-gray-400">{format(new Date(org.created_at), 'dd MMM yyyy')}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="flex items-center justify-between px-5 py-3 border-t">
          <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0} className="btn-secondary text-xs">Previous</button>
          <span className="text-xs text-gray-500">Page {page + 1}</span>
          <button onClick={() => setPage((p) => p + 1)} disabled={orgs.length < limit} className="btn-secondary text-xs">Next</button>
        </div>
      </div>
    </div>
  )
}
