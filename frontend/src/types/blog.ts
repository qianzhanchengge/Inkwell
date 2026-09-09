import type { Category, Tag } from './api'
import type { Article } from './article'

export interface BlogFeedParams {
  page?: number
  page_size?: number
  sort?: 'latest' | 'hot'
  /** 按分类筛选（博客分类浏览页使用） */
  category_id?: number
  /** 按标签名筛选（博客标签浏览页使用） */
  tag?: string
}

export interface HotArticle {
  id: number
  title: string
  summary?: string
  cover_image?: string
  view_count: number
  like_count: number
  published_at?: string | null
}

export interface CategoryStat extends Category {
  article_count?: number
}

export interface TagStat extends Tag {
  count?: number
}

export interface ArchiveItem {
  year: number
  month: number
  count: number
}

export interface RelatedArticle {
  id: number
  title: string
  summary?: string
  view_count: number
  like_count: number
}
