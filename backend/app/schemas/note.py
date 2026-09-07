"""笔记相关 Pydantic 模型。"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.tag import TagOut


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    category_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    is_pinned: bool = False


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None


class NoteDetail(BaseModel):
    id: int
    title: str
    content: str
    content_html: str
    category: Optional[dict] = None
    tags: List[TagOut] = Field(default_factory=list)
    is_pinned: bool
    word_count: int
    created_at: datetime
    updated_at: datetime


class NoteListItem(BaseModel):
    id: int
    title: str
    category_id: Optional[int]
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
