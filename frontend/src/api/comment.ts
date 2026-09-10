import blogRequest from './blogRequest'
import type { PageResult } from '@/types/api'
import type { Comment, CommentCreatePayload, CommentLikeResult } from '@/types/comment'

/** 评论列表为公开接口；带博客 token 时会返回 is_liked 等个性化字段 */
export function getComments(
  articleId: number | string,
  params?: { page?: number; page_size?: number }
): Promise<PageResult<Comment>> {
  return blogRequest.get(`/articles/${articleId}/comments`, { params })
}

/** 发表评论（需博客 token） */
export function createComment(
  articleId: number | string,
  data: CommentCreatePayload
): Promise<Comment> {
  return blogRequest.post(`/articles/${articleId}/comments`, data)
}

/** 删除评论（需博客 token，本人或文章作者） */
export function deleteComment(id: number | string): Promise<null> {
  return blogRequest.delete(`/comments/${id}`)
}

/** 评论点赞/取消（需博客 token） */
export function toggleCommentLike(id: number | string): Promise<CommentLikeResult> {
  return blogRequest.post(`/comments/${id}/like`)
}
