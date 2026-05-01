import api from '@/lib/api'

export interface AnalyticsOverview {
  // Backend field names from AnalyticsOverviewResponse
  org_id: string
  total_documents_processed: number
  total_pages_processed: number
  total_llm_tokens_input: number
  total_llm_tokens_output: number
  processing_success_count: number
  processing_failed_count: number
}

export interface DailyPoint {
  // Backend field names from DailyProcessingPoint
  day: string              // was: date
  documents_processed: number  // was: documents
  pages_processed: number
}

export const analyticsApi = {
  overview: () => api.get<AnalyticsOverview>('/analytics/overview'),

  dailyProcessing: (days = 30) =>
    api.get<{ org_id: string; points: DailyPoint[] }>(
      `/analytics/daily-processing?days=${days}`
    ),

  usageSummary: () =>
    api.get<Array<{ metric_type: string; total: number }>>('/usage/summary'),
}
