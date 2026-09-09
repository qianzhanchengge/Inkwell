import request from './request'
import type { PageResult } from '@/types/api'
import type { Article } from '@/types/article'

export interface FavoriteResult {
  favorited: boolean
}

export function toggleFavorite(articleId: number | string): Promise<FavoriteResult> {
  return request.post(`/articles/${articleId}/favorite`)
}

export function getFavorites(params?: {
  page?: number
  page_size?: number
}): Promise<PageResult<Article>> {
  return request.get('/favorites', { params })
}
