import request from './request'
import type { Article, ArticleCreatePayload, ArticleListParams } from '@/types/article'
import type { PageResult } from '@/types/api'

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

export function toggleArticleLike(id: number | string): Promise<Article> {
  return request.post(`/articles/${id}/like`)
}

export function searchArticles(keyword: string, params?: ArticleListParams): Promise<PageResult<Article>> {
  return request.get('/articles/search', { params: { ...params, keyword } })
}
