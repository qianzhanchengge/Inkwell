"""标签路由（§5.7）。"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user_id
from app.core.response import success
from app.schemas.tag import TagCreate, TagOut
from app.services import tag_service

router = APIRouter(prefix="/tags", tags=["标签"])


@router.get("")
async def list_tags(user_id: int = Depends(get_current_user_id)):
    tags = await tag_service.list_tags(user_id)
    return success([TagOut.model_validate(t).model_dump() for t in tags])


@router.post("")
async def create_tag(data: TagCreate, user_id: int = Depends(get_current_user_id)):
    tag = await tag_service.create_tag(user_id, data)
    return success(TagOut.model_validate(tag).model_dump())


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, user_id: int = Depends(get_current_user_id)):
    await tag_service.delete_tag(user_id, tag_id)
    return success()
