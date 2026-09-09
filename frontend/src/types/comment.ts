export interface CommentAuthor {
  id: number
  nickname: string
  avatar: string
}

export interface Comment {
  id: number
  article_id: number
  user_id: number
  parent_id: number | null
  reply_to_user_id: number | null
  content: string
  like_count: number
  status: number
  created_at: string
  updated_at: string
  // 后端聚合返回的作者信息
  author?: CommentAuthor | null
  reply_to_author?: CommentAuthor | null
  is_liked?: boolean
}

export interface CommentCreatePayload {
  content: string
  parent_id?: number | null
  reply_to_user_id?: number | null
}

export interface CommentLikeResult {
  liked: boolean
  like_count: number
}
