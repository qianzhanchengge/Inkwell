import request from './request'
import type { PageResult } from '@/types/api'
import type { Article } from '@/types/article'
import type {
  BlogFeedParams,
  HotArticle,
  CategoryStat,
  TagStat,
  ArchiveItem,
  RelatedArticle
} from '@/types/blog'

/** 兼容后端返回「数组」或「{items:[...]}」两种形态 */
function toArray<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[]
  if (data && typeof data === 'object' && Array.isArray((data as { items?: unknown[] }).items)) {
    return (data as { items: T[] }).items
  }
  return []
}

export function getBlogFeed(params: BlogFeedParams = {}): Promise<PageResult<Article>> {
  return request.get('/blog/feed', { params })
}

export async function getBlogHot(limit = 10): Promise<HotArticle[]> {
  const data = await request.get('/blog/hot', { params: { limit } })
  return toArray<HotArticle>(data)
}

export async function getBlogCategories(): Promise<CategoryStat[]> {
  const data = await request.get('/blog/categories')
  return toArray<CategoryStat>(data)
}

export async function getBlogTags(): Promise<TagStat[]> {
  const data = await request.get('/blog/tags')
  return toArray<TagStat>(data)
}

export async function getBlogArchive(): Promise<ArchiveItem[]> {
  const data = await request.get('/blog/archive')
  return toArray<ArchiveItem>(data)
}

export async function getRelatedArticles(
  articleId: number | string,
  limit = 5
): Promise<RelatedArticle[]> {
  const data = await request.get(`/blog/related/${articleId}`, { params: { limit } })
  return toArray<RelatedArticle>(data)
}
