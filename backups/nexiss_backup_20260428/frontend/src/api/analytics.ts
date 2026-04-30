import api from '@/lib/api'

export const analyticsApi = {
  overview: () =>
    api.get<{
      total_documents: number
      completed: number
      failed: number
      processing: number
      total_pages: number
      total_llm_tokens: number
    }>('/analytics/overview'),

  dailyProcessing: (days = 30) =>
    api.get<Array<{ date: string; documents: number; pages: number }>>(
      `/analytics/daily-processing?days=${days}`
    ),

  usageSummary: () =>
    api.get<Array<{ metric_type: string; total: number }>>('/usage/summary'),
}
