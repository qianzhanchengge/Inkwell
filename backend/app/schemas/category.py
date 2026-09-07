"""分类相关 Pydantic 模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: int = Field(..., ge=1, le=2)  # 1-笔记分类 2-文章分类
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None


class CategoryOut(BaseModel):
    id: int
    user_id: int
    name: str
    type: int
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}
