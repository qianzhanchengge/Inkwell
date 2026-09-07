"""标签路由（§5.7）。"""
from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import get_current_user_id
from app.core.exceptions import NotFoundException
from app.core.response import success
from app.database.mysql import get_session_factory
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagOut

router = APIRouter(prefix="/tags", tags=["标签"])


@router.get("")
async def list_tags(user_id: int = Depends(get_current_user_id)):
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(Tag).where(Tag.user_id == user_id))
        tags = result.scalars().all()
    return success([TagOut.model_validate(t).model_dump() for t in tags])


@router.post("")
async def create_tag(data: TagCreate, user_id: int = Depends(get_current_user_id)):
    factory = get_session_factory()
    async with factory() as session:
        tag = Tag(user_id=user_id, name=data.name)
        session.add(tag)
        await session.commit()
        await session.refresh(tag)
    return success(TagOut.model_validate(tag).model_dump())


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, user_id: int = Depends(get_current_user_id)):
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id))
        tag = result.scalar_one_or_none()
        if tag is None:
            raise NotFoundException("标签不存在")
        await session.delete(tag)
        await session.commit()
    return success()
