import request from './request'
import type { Tag } from '@/types/api'

export function getTagList(): Promise<Tag[]> {
  return request.get('/tags')
}

export function createTag(data: { name: string }): Promise<Tag> {
  return request.post('/tags', data)
}

export function deleteTag(id: number | string): Promise<null> {
  return request.delete(`/tags/${id}`)
}
