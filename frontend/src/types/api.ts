export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface Tag {
  id: number
  name: string
}

export interface Category {
  id: number
  name: string
  type: number
  sort_order?: number
}
