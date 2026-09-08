"""统计业务逻辑：概览与创作趋势（§5.8）。"""
from datetime import datetime, timedelta

from sqlalchemy import func, select

from app.database.mongodb import get_article_contents, get_note_contents
from app.database.mysql import get_session_factory
from app.database.redis import get_redis
from app.models.article import Article
from app.models.category import Category
from app.models.note import Note
from app.models.tag import Tag


async def _sum_word_count(collection, user_id: int) -> int:
    """遍历用户正文文档，累加 word_count（Python 侧求和，便于单测）。"""
    total = 0
    async for doc in collection.find({"user_id": user_id}):
        total += int(doc.get("word_count") or 0)
    return total


async def _redis_view_delta(article_ids: list) -> int:
    """累加 stat:article:view:{id} 中尚未回写 MySQL 的阅读量增量。

    按文档 §4.3 该键为 Hash；这里兼容 Hash（求和所有整数字段）与 String 两种
    形态，Redis 不可用或键不存在时返回 0（降级）。
    """
    try:
        redis = get_redis()
    except Exception:
        return 0
    delta = 0
    for aid in article_ids:
        key = f"stat:article:view:{aid}"
        try:
            hash_val = await redis.hgetall(key)
        except Exception:
            hash_val = None
        if hash_val:
            for v in hash_val.values():
                try:
                    delta += int(v)
                except (TypeError, ValueError):
                    pass
        else:
            try:
                s = await redis.get(key)
                if s is not None:
                    delta += int(s)
            except (TypeError, ValueError):
                pass
            except Exception:
                pass
    return delta


async def overview(user_id: int) -> dict:
    """概览统计：笔记/文章（分状态）/总字数/总阅读量/分类/标签。"""
    factory = get_session_factory()
    async with factory() as session:
        note_count = (
            await session.execute(
                select(func.count())
                .select_from(Note)
                .where(Note.user_id == user_id, Note.status == 1)
            )
        ).scalar_one()
        articles = (
            await session.execute(select(Article).where(Article.user_id == user_id))
        ).scalars().all()
        category_count = (
            await session.execute(
                select(func.count()).select_from(Category).where(Category.user_id == user_id)
            )
        ).scalar_one()
        tag_count = (
            await session.execute(
                select(func.count()).select_from(Tag).where(Tag.user_id == user_id)
            )
        ).scalar_one()

    article_count = len(articles)
    published_count = sum(1 for a in articles if a.status == 1)
    draft_count = sum(1 for a in articles if a.status == 0)
    total_views_mysql = sum(int(a.view_count or 0) for a in articles)
    article_ids = [a.id for a in articles]

    total_words = await _sum_word_count(
        get_note_contents(), user_id
    ) + await _sum_word_count(get_article_contents(), user_id)
    total_views = total_views_mysql + await _redis_view_delta(article_ids)

    return {
        "note_count": note_count,
        "article_count": article_count,
        "published_count": published_count,
        "draft_count": draft_count,
        "total_words": total_words,
        "total_views": total_views,
        "category_count": category_count,
        "tag_count": tag_count,
    }


async def trend(user_id: int, days: int) -> list:
    """近 N 天每日笔记/文章创建数，缺日补 0（按日期升序）。"""
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    buckets = {
        (start + timedelta(days=i)).isoformat(): {
            "date": (start + timedelta(days=i)).isoformat(),
            "note_count": 0,
            "article_count": 0,
        }
        for i in range(days)
    }

    since = datetime(start.year, start.month, start.day)
    factory = get_session_factory()
    async with factory() as session:
        notes = (
            await session.execute(
                select(Note).where(
                    Note.user_id == user_id, Note.status == 1, Note.created_at >= since
                )
            )
        ).scalars().all()
        articles = (
            await session.execute(
                select(Article).where(Article.user_id == user_id, Article.created_at >= since)
            )
        ).scalars().all()

    for n in notes:
        key = n.created_at.date().isoformat()
        if key in buckets:
            buckets[key]["note_count"] += 1
    for a in articles:
        key = a.created_at.date().isoformat()
        if key in buckets:
            buckets[key]["article_count"] += 1

    return [buckets[k] for k in sorted(buckets)]
