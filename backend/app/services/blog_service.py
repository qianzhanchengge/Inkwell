"""博客前台聚合业务（§5.5）。"""
from sqlalchemy import func, select

from app.core.exceptions import NotFoundException
from app.database.mysql import get_session_factory
from app.models.article import Article, article_tags
from app.models.category import Category
from app.models.tag import Tag


def _article_item(a: Article) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "summary": a.summary or "",
        "cover_image": a.cover_image or "",
        "view_count": a.view_count or 0,
        "like_count": a.like_count or 0,
        "published_at": a.published_at,
        "created_at": a.created_at,
    }


async def feed(
    page: int,
    page_size: int,
    sort: str = "latest",
    category_id: int | None = None,
    tag: str | None = None,
) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(Article).where(Article.status == 1)
        if category_id is not None:
            stmt = stmt.where(Article.category_id == category_id)
        if tag:
            # 标签按名称匹配（同名标签可能属于不同用户，取全部 id 再筛选）
            tag_ids = [
                t.id
                for t in (
                    await session.execute(select(Tag).where(Tag.name == tag))
                ).scalars().all()
            ]
            if not tag_ids:
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0,
                }
            stmt = stmt.where(
                Article.id.in_(
                    select(article_tags.c.article_id).where(
                        article_tags.c.tag_id.in_(list(tag_ids))
                    )
                )
            )
        if sort == "hot":
            stmt = stmt.order_by(
                (Article.view_count + Article.like_count * 10).desc(),
                Article.published_at.desc(),
            )
        else:
            stmt = stmt.order_by(Article.published_at.desc(), Article.id.desc())

        total = (
            await session.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar_one()
        result = await session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        items = [_article_item(a) for a in result.scalars().all()]
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


async def hot(top_n: int) -> list:
    factory = get_session_factory()
    async with factory() as session:
        stmt = (
            select(Article)
            .where(Article.status == 1)
            .order_by((Article.view_count + Article.like_count * 10).desc())
            .limit(top_n)
        )
        result = await session.execute(stmt)
        return [_article_item(a) for a in result.scalars().all()]


async def category_stats() -> list:
    factory = get_session_factory()
    async with factory() as session:
        cats = (
            await session.execute(select(Category).where(Category.type == 2))
        ).scalars().all()
        out = []
        for c in cats:
            count = (
                await session.execute(
                    select(func.count()).select_from(
                        select(Article)
                        .where(Article.category_id == c.id, Article.status == 1)
                        .subquery()
                    )
                )
            ).scalar_one()
            out.append({"id": c.id, "name": c.name, "article_count": count})
        return out


async def tag_cloud() -> list:
    factory = get_session_factory()
    async with factory() as session:
        articles = (
            await session.execute(select(Article).where(Article.status == 1))
        ).scalars().all()
        counter: dict = {}
        for a in articles:
            for t in (a.tags or []):
                counter[t.id] = counter.get(t.id, 0) + 1

        tags = (await session.execute(select(Tag))).scalars().all()
        out = [
            {"id": t.id, "name": t.name, "use_count": counter.get(t.id, 0)}
            for t in tags
        ]
        out.sort(key=lambda x: (-x["use_count"], x["name"]))
        return out


async def archive() -> list:
    factory = get_session_factory()
    async with factory() as session:
        articles = (
            await session.execute(select(Article).where(Article.status == 1))
        ).scalars().all()
        buckets: dict = {}
        for a in articles:
            dt = a.published_at or a.created_at
            if dt is None:
                continue
            key = (dt.year, dt.month)
            buckets[key] = buckets.get(key, 0) + 1
        out = [{"year": y, "month": m, "count": c} for (y, m), c in buckets.items()]
        out.sort(key=lambda x: (-x["year"], -x["month"]))
        return out


async def related(article_id: int, top_n: int) -> list:
    factory = get_session_factory()
    async with factory() as session:
        article = (
            await session.execute(select(Article).where(Article.id == article_id))
        ).scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")

        candidates = (
            await session.execute(
                select(Article).where(Article.status == 1, Article.id != article_id)
            )
        ).scalars().all()

        current_tag_ids = {t.id for t in (article.tags or [])}
        scored = []
        for a in candidates:
            score = 0
            if a.category_id and a.category_id == article.category_id:
                score += 2
            a_tag_ids = {t.id for t in (a.tags or [])}
            score += len(a_tag_ids & current_tag_ids)
            if score > 0:
                scored.append((score, a))
        scored.sort(key=lambda x: -x[0])
        return [_article_item(a) for _, a in scored[:top_n]]
