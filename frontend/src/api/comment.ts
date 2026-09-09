import request from './request'
import type { PageResult } from '@/types/api'
import type { Comment, CommentCreatePayload, CommentLikeResult } from '@/types/comment'

export function getComments(
  articleId: number | string,
  params?: { page?: number; page_size?: number }
): Promise<PageResult<Comment>> {
  return request.get(`/articles/${articleId}/comments`, { params })
}

export function createComment(
  articleId: number | string,
  data: CommentCreatePayload
): Promise<Comment> {
  return request.post(`/articles/${articleId}/comments`, data)
}

export function deleteComment(id: number | string): Promise<null> {
  return request.delete(`/comments/${id}`)
}

export function toggleCommentLike(id: number | string): Promise<CommentLikeResult> {
  return request.post(`/comments/${id}/like`)
}
