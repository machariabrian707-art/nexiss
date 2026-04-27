import api from '@/lib/api'

export const exportApi = {
  exportDocuments: (format: 'csv' | 'xlsx', params?: { doc_type?: string; status?: string }) =>
    api.get(`/export/documents?format=${format}`, {
      params,
      responseType: 'blob',
    }),
}
