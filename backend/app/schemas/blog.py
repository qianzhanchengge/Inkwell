"""博客前台聚合接口的 Pydantic 模型（§5.5）。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FeedQuery(BaseModel):
    sort: str = Field("latest", pattern="^(latest|hot)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class BlogArticleItem(BaseModel):
    id: int
    title: str
    summary: str
    cover_image: str
    view_count: int
    like_count: int
    published_at: Optional[datetime]
    created_at: datetime


class CategoryStat(BaseModel):
    id: int
    name: str
    article_count: int


class TagStat(BaseModel):
    id: int
    name: str
    use_count: int


class ArchiveItem(BaseModel):
    year: int
    month: int
    count: int
