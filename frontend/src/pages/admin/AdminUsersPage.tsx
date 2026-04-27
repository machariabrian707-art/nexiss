import { useQuery } from '@tanstack/react-query'
import { adminApi } from '@/api/admin'
import { Users } from 'lucide-react'
import { format } from 'date-fns'
import { useState } from 'react'

export default function AdminUsersPage() {
  const [page, setPage] = useState(0)
  const limit = 20

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'users', page],
    queryFn: () => adminApi.users({ skip: page * limit, limit }).then((r) => r.data),
  })

  const users: Array<{
    id: string; full_name: string; email: string;
    is_superadmin: boolean; created_at: string; org_name?: string
  }> = Array.isArray(data) ? data : []

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2">
        <Users size={22} className="text-brand-500" />
        <h1 className="text-2xl font-bold text-gray-900">Users</h1>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b">
              <th className="text-left px-5 py-3 font-medium text-gray-500">Name</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Email</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Organisation</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Role</th>
              <th className="text-left px-5 py-3 font-medium text-gray-500">Joined</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {isLoading && <tr><td colSpan={5} className="px-5 py-10 text-center text-gray-400">Loading...</td></tr>}
            {!isLoading && users.length === 0 && <tr><td colSpan={5} className="px-5 py-10 text-center text-gray-400">No users yet.</td></tr>}
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-5 py-3.5 font-medium text-gray-900">{u.full_name}</td>
                <td className="px-5 py-3.5 text-gray-500">{u.email}</td>
                <td className="px-5 py-3.5 text-gray-500">{u.org_name ?? '—'}</td>
                <td className="px-5 py-3.5">
                  {u.is_superadmin
                    ? <span className="badge bg-purple-100 text-purple-700">Super Admin</span>
                    : <span className="badge-gray">Member</span>}
                </td>
                <td className="px-5 py-3.5 text-gray-400">{format(new Date(u.created_at), 'dd MMM yyyy')}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="flex items-center justify-between px-5 py-3 border-t">
          <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0} className="btn-secondary text-xs">Previous</button>
          <span className="text-xs text-gray-500">Page {page + 1}</span>
          <button onClick={() => setPage((p) => p + 1)} disabled={users.length < limit} className="btn-secondary text-xs">Next</button>
        </div>
      </div>
    </div>
  )
}
