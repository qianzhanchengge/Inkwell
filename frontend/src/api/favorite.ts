import blogRequest from './blogRequest'
import type { PageResult } from '@/types/api'
import type { Article } from '@/types/article'

export interface FavoriteResult {
  favorited: boolean
}

/** 收藏/取消收藏（需博客 token） */
export function toggleFavorite(articleId: number | string): Promise<FavoriteResult> {
  return blogRequest.post(`/articles/${articleId}/favorite`)
}

/** 我的收藏（需博客 token） */
export function getFavorites(params?: {
  page?: number
  page_size?: number
}): Promise<PageResult<Article>> {
  return blogRequest.get('/articles/favorites', { params })
}
