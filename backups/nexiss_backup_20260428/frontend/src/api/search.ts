import api from '@/lib/api'

export const searchApi = {
  search: (q: string, params?: { doc_type?: string; org_id?: string }) =>
    api.get('/search', { params: { q, ...params } }),
}
