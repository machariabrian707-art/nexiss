import api from '@/lib/api'

export const adminApi = {
  stats: () =>
    api.get<{
      total_orgs: number
      total_users: number
      total_documents: number
      documents_today: number
      failed_documents: number
      processing_queue: number
    }>('/admin/stats'),

  orgs: (params?: { skip?: number; limit?: number }) =>
    api.get('/admin/orgs', { params }),

  users: (params?: { skip?: number; limit?: number }) =>
    api.get('/admin/users', { params }),

  documents: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/admin/documents', { params }),

  reprocessDocument: (id: string) =>
    api.post(`/admin/documents/${id}/reprocess`),
}
