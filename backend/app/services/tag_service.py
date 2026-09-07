"""标签业务逻辑。"""
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag


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
