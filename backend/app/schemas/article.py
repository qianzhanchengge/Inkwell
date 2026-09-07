"""文章相关 Pydantic 模型。"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.tag import TagOut


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    summary: str = Field("", max_length=500)
    content: str
    cover_image: str = ""
    category_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None


class ArticleDetail(BaseModel):
    id: int
    title: str
    summary: str
    content: str
    content_html: str
    cover_image: str
    category: Optional[dict] = None
    tags: List[TagOut] = Field(default_factory=list)
    view_count: int
    like_count: int
    status: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ArticleListItem(BaseModel):
    id: int
    title: str
    summary: str
    cover_image: str
    category_id: Optional[int]
    view_count: int
    like_count: int
    status: int
    published_at: Optional[datetime]
    created_at: datetime
