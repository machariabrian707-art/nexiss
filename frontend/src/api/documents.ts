import api from '@/lib/api'

export type DocStatus = 'uploaded' | 'processing' | 'completed' | 'failed'

export interface Document {
  id: string
  filename: string
  doc_type: string | null
  status: DocStatus
  page_count: number | null
  created_at: string
  updated_at: string
  extraction_result: Record<string, unknown> | null
  org_id: string
}

export interface DocumentProgress {
  job_id: string
  status: string
  step: string
  progress_pct: number
  error: string | null
}

export const documentsApi = {
  list: (params?: { skip?: number; limit?: number; status?: string; doc_type?: string }) =>
    api.get<Document[]>('/documents', { params }),

  get: (id: string) =>
    api.get<Document>(`/documents/${id}`),

  create: (data: { s3_key: string; filename: string; doc_type_hint?: string }) =>
    api.post<Document>('/documents', data),

  process: (id: string) =>
    api.post(`/documents/${id}/process`),

  retry: (id: string) =>
    api.post(`/documents/${id}/retry`),

  progress: (id: string) =>
    api.get<DocumentProgress>(`/documents/${id}/progress`),

  signedUpload: (filename: string, content_type: string) =>
    api.post<{ upload_url: string; s3_key: string }>('/storage/signed-upload', { filename, content_type }),

  signedDownload: (s3_key: string) =>
    api.post<{ download_url: string }>('/storage/signed-download', { s3_key }),
}
