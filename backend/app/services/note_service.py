"""笔记业务逻辑（§6.3.1 创建流程）。"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select

from app.core.cache import cache_invalidate_pattern
from app.core.exceptions import ForbiddenException, NotFoundException
from app.database.mongodb import get_note_contents
from app.database.mysql import get_session_factory
from app.models.category import Category
from app.models.note import Note, note_tags
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.tag_service import get_or_create_tags
from app.utils.markdown import count_words, markdown_to_html


async def _build_note_detail(session, note: Note) -> dict:
    collection = get_note_contents()
    content_doc = await collection.find_one({"note_id": note.id})
    content = content_doc["content"] if content_doc else ""
    content_html = content_doc["content_html"] if content_doc else ""
    word_count = content_doc["word_count"] if content_doc else 0

    tags = [{"id": t.id, "name": t.name} for t in (note.tags or [])]
    category = None
    if note.category_id:
        cat_result = await session.execute(select(Category).where(Category.id == note.category_id))
        cat = cat_result.scalar_one_or_none()
        if cat is not None:
            category = {"id": cat.id, "name": cat.name}
    return {
        "id": note.id,
        "title": note.title,
        "content": content,
        "content_html": content_html,
        "category": category,
        "tags": tags,
        "is_pinned": bool(note.is_pinned),
        "word_count": word_count,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }


async def create_note(user_id: int, data: NoteCreate) -> dict:
    content_html = markdown_to_html(data.content)
    word_count = count_words(data.content)

    # 1. 写入 MongoDB，获得 content_id
    collection = get_note_contents()
    doc = await collection.insert_one(
        {
            "user_id": user_id,
            "content": data.content,
            "content_html": content_html,
            "word_count": word_count,
            "version": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )
    content_id = str(doc.inserted_id)

    # 2. 写入 MySQL（事务）
    factory = get_session_factory()
    async with factory() as session:
        async with session.begin():
            note = Note(
                user_id=user_id,
                title=data.title,
                content_id=content_id,
                category_id=data.category_id,
                is_pinned=1 if data.is_pinned else 0,
            )
            session.add(note)
            await session.flush()

            if data.tags:
                tag_ids = await get_or_create_tags(session, user_id, data.tags)
                for tag_id in tag_ids:
                    await session.execute(
                        note_tags.insert().values(note_id=note.id, tag_id=tag_id)
                    )
        await session.refresh(note)

    # 回写 note_id 到 MongoDB
    await collection.update_one({"_id": doc.inserted_id}, {"$set": {"note_id": note.id}})

    # 3. 清除缓存
    await cache_invalidate_pattern(f"cache:notes:list:{user_id}:*")

    return await _build_note_detail(session, note)


async def list_notes(
    user_id: int,
    page: int,
    page_size: int,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(Note).where(Note.user_id == user_id, Note.status == 1)
        if category_id is not None:
            stmt = stmt.where(Note.category_id == category_id)
        if keyword:
            stmt = stmt.where(Note.title.like(f"%{keyword}%"))

        total = (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
        result = await session.execute(
            stmt.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        notes = result.scalars().all()
        items = [
            {
                "id": n.id,
                "title": n.title,
                "category_id": n.category_id,
                "is_pinned": bool(n.is_pinned),
                "created_at": n.created_at,
                "updated_at": n.updated_at,
            }
            for n in notes
        ]
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


async def search_notes(user_id: int, keyword: str, page: int, page_size: int) -> dict:
    """全文搜索：MongoDB 正则匹配正文，再回查 MySQL 元数据。"""
    import re

    collection = get_note_contents()
    note_ids = []
    cursor = collection.find(
        {"user_id": user_id, "content": {"$regex": re.escape(keyword), "$options": "i"}}
    )
    async for doc in cursor:
        if doc.get("note_id"):
            note_ids.append(doc["note_id"])

    if not note_ids:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
        }

    factory = get_session_factory()
    async with factory() as session:
        stmt = select(Note).where(Note.id.in_(note_ids), Note.status == 1)
        result = await session.execute(
            stmt.order_by(Note.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        notes = result.scalars().all()
        items = [
            {
                "id": n.id,
                "title": n.title,
                "category_id": n.category_id,
                "is_pinned": bool(n.is_pinned),
                "created_at": n.created_at,
                "updated_at": n.updated_at,
            }
            for n in notes
        ]
        return {
            "items": items,
            "total": len(note_ids),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(note_ids) + page_size - 1) // page_size,
        }


async def get_note(user_id: int, note_id: int) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id, Note.status == 1)
        )
        note = result.scalar_one_or_none()
        if note is None:
            raise NotFoundException("笔记不存在")
        return await _build_note_detail(session, note)


async def update_note(user_id: int, note_id: int, data: NoteUpdate) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id, Note.status == 1)
        )
        note = result.scalar_one_or_none()
        if note is None:
            raise NotFoundException("笔记不存在")

        if data.title is not None:
            note.title = data.title
        if data.category_id is not None:
            note.category_id = data.category_id
        if data.is_pinned is not None:
            note.is_pinned = 1 if data.is_pinned else 0

        if data.content is not None:
            collection = get_note_contents()
            await collection.update_one(
                {"note_id": note.id},
                {
                    "$set": {
                        "content": data.content,
                        "content_html": markdown_to_html(data.content),
                        "word_count": count_words(data.content),
                        "updated_at": datetime.now(timezone.utc),
                    },
                    "$inc": {"version": 1},
                },
            )

        if data.tags is not None:
            await session.execute(note_tags.delete().where(note_tags.c.note_id == note.id))
            tag_ids = await get_or_create_tags(session, user_id, data.tags)
            for tag_id in tag_ids:
                await session.execute(note_tags.insert().values(note_id=note.id, tag_id=tag_id))

        await session.commit()
        await session.refresh(note)
        await cache_invalidate_pattern(f"cache:notes:list:{user_id}:*")
        return await _build_note_detail(session, note)


async def delete_note(user_id: int, note_id: int) -> None:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(Note).where(Note.id == note_id, Note.user_id == user_id))
        note = result.scalar_one_or_none()
        if note is None:
            raise NotFoundException("笔记不存在")
        note.status = 0  # 软删除
        await session.commit()
        await cache_invalidate_pattern(f"cache:notes:list:{user_id}:*")


async def toggle_pin(user_id: int, note_id: int) -> bool:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(Note).where(Note.id == note_id, Note.user_id == user_id))
        note = result.scalar_one_or_none()
        if note is None:
            raise NotFoundException("笔记不存在")
        note.is_pinned = 0 if note.is_pinned else 1
        await session.commit()
        await cache_invalidate_pattern(f"cache:notes:list:{user_id}:*")
        return bool(note.is_pinned)
