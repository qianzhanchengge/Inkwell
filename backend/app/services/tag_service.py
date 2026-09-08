"""标签业务逻辑（§5.7）。"""
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.database.mysql import get_session_factory
from app.models.article import article_tags
from app.models.note import note_tags
from app.models.tag import Tag
from app.schemas.tag import TagCreate


async def get_or_create_tags(session: AsyncSession, user_id: int, names: List[str]) -> List[int]:
    """查找或创建标签，返回标签 ID 列表（在事务内使用）。"""
    tag_ids: List[int] = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        result = await session.execute(
            select(Tag).where(Tag.user_id == user_id, Tag.name == name)
        )
        tag = result.scalar_one_or_none()
        if tag is None:
            tag = Tag(user_id=user_id, name=name)
            session.add(tag)
            await session.flush()
        tag_ids.append(tag.id)
    return tag_ids


async def list_tags(user_id: int) -> List[Tag]:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(Tag).where(Tag.user_id == user_id))
        return list(result.scalars().all())


async def create_tag(user_id: int, data: TagCreate) -> Tag:
    factory = get_session_factory()
    async with factory() as session:
        # 已存在同名标签则直接返回，避免违反 uk_user_tag 唯一约束
        result = await session.execute(
            select(Tag).where(Tag.user_id == user_id, Tag.name == data.name)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

        tag = Tag(user_id=user_id, name=data.name)
        session.add(tag)
        await session.commit()
        await session.refresh(tag)
        return tag


async def delete_tag(user_id: int, tag_id: int) -> None:
    """删除标签；删除前清理其在笔记/文章上的关联。"""
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        )
        tag = result.scalar_one_or_none()
        if tag is None:
            raise NotFoundException("标签不存在")

        await session.execute(delete(note_tags).where(note_tags.c.tag_id == tag_id))
        await session.execute(delete(article_tags).where(article_tags.c.tag_id == tag_id))

        await session.delete(tag)
        await session.commit()
