"""分类路由（§5.6）。"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user_id
from app.core.response import success
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["分类"])


@router.get("")
async def list_categories(
    type: Optional[int] = Query(None, ge=1, le=2),
    user_id: int = Depends(get_current_user_id),
):
    categories = await category_service.list_categories(user_id, type)
    return success([CategoryOut.model_validate(c).model_dump() for c in categories])


@router.post("")
async def create_category(data: CategoryCreate, user_id: int = Depends(get_current_user_id)):
    category = await category_service.create_category(user_id, data)
    return success(CategoryOut.model_validate(category).model_dump())


@router.put("/{category_id}")
async def update_category(
    category_id: int, data: CategoryUpdate, user_id: int = Depends(get_current_user_id)
):
    category = await category_service.update_category(user_id, category_id, data)
    return success(CategoryOut.model_validate(category).model_dump())


@router.delete("/{category_id}")
async def delete_category(category_id: int, user_id: int = Depends(get_current_user_id)):
    await category_service.delete_category(user_id, category_id)
    return success()
