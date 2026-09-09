"""评论相关 Pydantic 模型（§5.1）。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    parent_id: Optional[int] = None
    reply_to_user_id: Optional[int] = None


class CommentOut(BaseModel):
    id: int
    article_id: int
    user_id: int
    author_nickname: str
    author_avatar: str
    parent_id: Optional[int]
    reply_to_user_id: Optional[int]
    reply_to_nickname: Optional[str]
    content: str
    like_count: int
    created_at: datetime
