import api from '@/lib/api'

export type DocStatus = 'uploaded' | 'processing' | 'completed' | 'failed'

// Matches backend DocumentResponse exactly
export interface Document {
  id: string
  org_id: string
  created_by_user_id: string | null
  file_name: string          // was: filename
  content_type: string
  storage_key: string        // was: s3_key
  status: DocStatus
  page_count: number | null
  extracted_data: Record<string, unknown> | null  // was: extraction_result
  confidence_score: string | null
  processing_attempts: number
  last_error: string | null
  declared_type: string | null    // was: doc_type_hint
  confirmed_type: string | null   // was: doc_type
  document_subtype: string | null
  type_confidence: string | null
  created_at: string
  updated_at: string
}

// Matches backend DocumentProgressResponse exactly
export interface DocumentProgress {
  job_id: string
  document_id: string
  status: string
  current_step: string       // was: step
  progress_percentage: number  // was: progress_pct
  error_message: string | null // was: error
  task_id: string
  updated_at: string
}

// Matches backend DocumentSearchResponse
export interface DocumentSearchResult {
  id: string
  file_name: string
  status: DocStatus
  confirmed_type: string | null
  document_subtype: string | null
  declared_type: string | null
  page_count: number | null
  created_at: string
}

export const documentsApi = {
  list: (params?: { limit?: number; offset?: number; status?: string }) =>
    api.get<Document[]>('/documents', { params }),

  get: (id: string) =>
    api.get<Document>(`/documents/${id}`),

  // Matches backend DocumentCreateRequest
  create: (data: {
    file_name: string        // was: filename
    content_type: string
    storage_key: string      // was: s3_key
    declared_type?: string   // was: doc_type_hint
    declared_subtype?: string
  }) => api.post<Document>('/documents', data),

  process: (id: string) =>
    api.post(`/documents/${id}/process`),

  retry: (id: string) =>
    api.post(`/documents/${id}/retry`),

  progress: (id: string) =>
    api.get<DocumentProgress>(`/documents/${id}/progress`),

  search: (params: {
    q?: string
    doc_type?: string
    entity_name?: string
    status?: string
    limit?: number
  }) => api.get<DocumentSearchResult[]>('/documents/search', { params }),

  entities: (id: string) =>
    api.get<Array<{ id: string; canonical_name: string; entity_kind: string; created_at: string }>>(
      `/documents/${id}/entities`
    ),

  // Matches backend SignedUploadRequest: { file_name, content_type }
  signedUpload: (file_name: string, content_type: string) =>
    api.post<{ storage_key: string; upload_url: string; expires_in_seconds: number }>(
      '/storage/signed-upload',
      { file_name, content_type }   // was: { filename, content_type } — filename != file_name
    ),

  signedDownload: (storage_key: string) =>
    api.post<{ storage_key: string; download_url: string; expires_in_seconds: number }>(
      '/storage/signed-download',
      { storage_key }   // was: { s3_key }
    ),

  exportXlsx: (doc_type?: string) => {
    const params = doc_type ? `?doc_type=${doc_type}` : ''
    return api.get(`/export/documents.xlsx${params}`, { responseType: 'blob' })
  },
}
