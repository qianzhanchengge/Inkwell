import type { Category, Tag } from './api'

export interface Article {
  id: number
  title: string
  summary: string
  content: string
  content_html?: string
  cover_image?: string
  category?: Category | null
  tags?: Tag[]
  view_count: number
  like_count: number
  status: number
  published_at?: string | null
  created_at: string
  updated_at: string
}

export interface ArticleCreatePayload {
  title: string
  summary?: string
  content: string
  cover_image?: string
  category_id?: number | null
  tags?: string[]
}

export interface ArticleListParams {
  page?: number
  page_size?: number
  status?: number
  keyword?: string
}
