import request from './request'
import type { Category } from '@/types/api'

export function getCategoryList(type: 1 | 2): Promise<Category[]> {
  return request.get('/categories', { params: { type } })
}

export function createCategory(data: { name: string; type: number; sort_order?: number }): Promise<Category> {
  return request.post('/categories', data)
}

export function updateCategory(id: number | string, data: { name: string; sort_order?: number }): Promise<Category> {
  return request.put(`/categories/${id}`, data)
}

export function deleteCategory(id: number | string): Promise<null> {
  return request.delete(`/categories/${id}`)
}
