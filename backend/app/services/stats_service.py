"""统计业务逻辑：概览与创作趋势。"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.database.mysql import get_session_factory
from app.models.article import Article
from app.models.note import Note


async def overview(user_id: int) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        note_count = (
            await session.execute(
                select(func.count()).select_from(Note).where(Note.user_id == user_id, Note.status == 1)
            )
        ).scalar_one()
        article_count = (
            await session.execute(
                select(func.count()).select_from(Article).where(Article.user_id == user_id)
            )
        ).scalar_one()
        published_count = (
            await session.execute(
                select(func.count()).select_from(Article).where(Article.user_id == user_id, Article.status == 1)
            )
        ).scalar_one()
        total_views = (
            await session.execute(
                select(func.coalesce(func.sum(Article.view_count), 0)).where(Article.user_id == user_id)
            )
        ).scalar_one()

    return {
        "note_count": note_count,
        "article_count": article_count,
        "published_count": published_count,
        "total_views": total_views,
    }


async def trend(user_id: int, days: int) -> list:
    """近 N 天每日创建数（笔记+文章）。"""
    factory = get_session_factory()
    async with factory() as session:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        note_rows = (
            await session.execute(
                select(func.date(Note.created_at), func.count())
                .where(Note.user_id == user_id, Note.created_at >= since)
                .group_by(func.date(Note.created_at))
            )
        ).all()
        article_rows = (
            await session.execute(
                select(func.date(Article.created_at), func.count())
                .where(Article.user_id == user_id, Article.created_at >= since)
                .group_by(func.date(Article.created_at))
            )
        ).all()

    by_date: dict[str, dict] = {}
    for day, count in note_rows:
        key = str(day)
        by_date.setdefault(key, {"date": key, "note_count": 0, "article_count": 0})
        by_date[key]["note_count"] += count
    for day, count in article_rows:
        key = str(day)
        by_date.setdefault(key, {"date": key, "note_count": 0, "article_count": 0})
        by_date[key]["article_count"] += count

    return sorted(by_date.values(), key=lambda x: x["date"])
