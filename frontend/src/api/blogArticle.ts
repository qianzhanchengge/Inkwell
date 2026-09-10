import blogRequest from './blogRequest'
import type { Article, ArticleListParams, LikeResult } from '@/types/article'
import type { PageResult } from '@/types/api'

/**
 * 博客侧文章接口（公开读 + 博客 scope 互动）。
 * 工作台的文章管理接口在 `api/article.ts`，两者请求实例与令牌互相独立。
 */
export function getBlogArticleList(params: ArticleListParams): Promise<PageResult<Article>> {
  return blogRequest.get('/articles', { params })
}

export function getBlogArticle(id: number | string): Promise<Article> {
  return blogRequest.get(`/articles/${id}`)
}

export function searchBlogArticles(
  keyword: string,
  params?: ArticleListParams
): Promise<PageResult<Article>> {
  return blogRequest.get('/articles/search', { params: { ...params, keyword } })
}

export function toggleBlogArticleLike(id: number | string): Promise<LikeResult> {
  return blogRequest.post(`/articles/${id}/like`)
}

export function getBlogArticleLikeStatus(id: number | string): Promise<{ liked: boolean }> {
  return blogRequest.get(`/articles/${id}/like`)
}
