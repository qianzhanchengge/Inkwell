import type { Category, Tag } from './api'

export interface Note {
  id: number
  title: string
  content: string
  content_html?: string
  category?: Category | null
  tags?: Tag[]
  is_pinned: boolean
  word_count?: number
  created_at: string
  updated_at: string
}

export interface NoteListParams {
  page?: number
  page_size?: number
  category_id?: number
  tag_id?: number
  keyword?: string
}

export interface NoteCreatePayload {
  title: string
  content: string
  category_id?: number | null
  tags?: string[]
  is_pinned?: boolean
}
