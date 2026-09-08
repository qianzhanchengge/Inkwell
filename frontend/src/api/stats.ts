import request from './request'

export interface StatsOverview {
  note_count: number
  article_count: number
  published_count: number
  draft_count: number
  total_words: number
  total_views: number
  category_count: number
  tag_count: number
}

export interface TrendItem {
  date: string
  note_count: number
  article_count: number
}

export function getStatsOverview(): Promise<StatsOverview> {
  return request.get('/stats/overview')
}

export function getStatsTrend(days = 30): Promise<TrendItem[]> {
  return request.get('/stats/trend', { params: { days } })
}
