import type { Category, Tag } from './api'

export interface ArticleAuthor {
  id: number
  nickname: string
  avatar: string
}

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
  // 博客系统新增互动字段（详情接口返回）
  author?: ArticleAuthor | null
  comment_count?: number
  share_count?: number
  is_liked?: boolean
  is_favorited?: boolean
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

export interface LikeResult {
  liked: boolean
  like_count: number
}
