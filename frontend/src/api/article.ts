import request from './request'
import type { Article, ArticleCreatePayload, ArticleListParams } from '@/types/article'
import type { PageResult } from '@/types/api'

// 工作台（后台）文章管理接口（workbench scope）。
// 博客前台的公开读与点赞/收藏/分享接口在 `api/blogArticle.ts` / `api/favorite.ts` / `api/share.ts`。

export function getArticleList(params: ArticleListParams): Promise<PageResult<Article>> {
  return request.get('/articles', { params })
}

export function getMyArticles(params: ArticleListParams): Promise<PageResult<Article>> {
  return request.get('/articles/mine', { params })
}

export function getArticle(id: number | string): Promise<Article> {
  return request.get(`/articles/${id}`)
}

export function createArticle(data: ArticleCreatePayload): Promise<Article> {
  return request.post('/articles', data)
}

export function updateArticle(id: number | string, data: ArticleCreatePayload): Promise<Article> {
  return request.put(`/articles/${id}`, data)
}

export function deleteArticle(id: number | string): Promise<null> {
  return request.delete(`/articles/${id}`)
}

export function publishArticle(id: number | string): Promise<Article> {
  return request.post(`/articles/${id}/publish`)
}

export function unpublishArticle(id: number | string): Promise<Article> {
  return request.post(`/articles/${id}/unpublish`)
}

export function searchArticles(keyword: string, params?: ArticleListParams): Promise<PageResult<Article>> {
  return request.get('/articles/search', { params: { ...params, keyword } })
}
