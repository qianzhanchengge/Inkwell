"""文章业务逻辑（§6.3.2 发布流程）。"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select

from app.core.cache import cache_invalidate_pattern
from app.core.exceptions import APIException, ForbiddenException, NotFoundException
from app.database.mongodb import get_article_contents
from app.database.mysql import get_session_factory
from app.models.article import Article, article_tags
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.services.tag_service import get_or_create_tags
from app.utils.markdown import count_words, estimate_reading_time, markdown_to_html


async def _build_article_detail(session, article: Article) -> dict:
    collection = get_article_contents()
    content_doc = await collection.find_one({"article_id": article.id})
    content = content_doc["content"] if content_doc else ""
    content_html = content_doc["content_html"] if content_doc else ""

    tags = [{"id": t.id, "name": t.name} for t in (article.tags or [])]
    return {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "content": content,
        "content_html": content_html,
        "cover_image": article.cover_image,
        "category": {"id": article.category_id} if article.category_id else None,
        "tags": tags,
        "view_count": article.view_count,
        "like_count": article.like_count,
        "status": article.status,
        "published_at": article.published_at,
        "created_at": article.created_at,
        "updated_at": article.updated_at,
    }


async def create_article(user_id: int, data: ArticleCreate) -> dict:
    content_html = markdown_to_html(data.content)
    word_count = count_words(data.content)

    collection = get_article_contents()
    doc = await collection.insert_one(
        {
            "user_id": user_id,
            "content": data.content,
            "content_html": content_html,
            "word_count": word_count,
            "reading_time": estimate_reading_time(word_count),
            "version": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )
    content_id = str(doc.inserted_id)

    factory = get_session_factory()
    async with factory() as session:
        async with session.begin():
            article = Article(
                user_id=user_id,
                title=data.title,
                summary=data.summary,
                content_id=content_id,
                cover_image=data.cover_image,
                category_id=data.category_id,
                status=0,  # 草稿
            )
            session.add(article)
            await session.flush()

            if data.tags:
                tag_ids = await get_or_create_tags(session, user_id, data.tags)
                for tag_id in tag_ids:
                    await session.execute(
                        article_tags.insert().values(article_id=article.id, tag_id=tag_id)
                    )
        await session.refresh(article)

    await collection.update_one({"_id": doc.inserted_id}, {"$set": {"article_id": article.id}})
    return await _build_article_detail(session, article)


async def list_articles(
    user_id: Optional[int],
    page: int,
    page_size: int,
    status: Optional[int] = None,
    public_only: bool = False,
) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(Article)
        if public_only:
            stmt = stmt.where(Article.status == 1)  # 仅已发布
        elif user_id is not None:
            stmt = stmt.where(Article.user_id == user_id)
        if status is not None:
            stmt = stmt.where(Article.status == status)

        total = (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
        result = await session.execute(
            stmt.order_by(Article.published_at.desc(), Article.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        articles = result.scalars().all()
        items = [
            {
                "id": a.id,
                "title": a.title,
                "summary": a.summary,
                "cover_image": a.cover_image,
                "category_id": a.category_id,
                "view_count": a.view_count,
                "like_count": a.like_count,
                "status": a.status,
                "published_at": a.published_at,
                "created_at": a.created_at,
            }
            for a in articles
        ]
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


async def search_articles(keyword: str, page: int, page_size: int) -> dict:
    """公开全文搜索：MongoDB 正则匹配正文，仅返回已发布文章。"""
    import re

    collection = get_article_contents()
    article_ids = []
    cursor = collection.find(
        {"content": {"$regex": re.escape(keyword), "$options": "i"}}
    )
    async for doc in cursor:
        if doc.get("article_id"):
            article_ids.append(doc["article_id"])

    if not article_ids:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
        }

    factory = get_session_factory()
    async with factory() as session:
        stmt = select(Article).where(Article.id.in_(article_ids), Article.status == 1)
        result = await session.execute(
            stmt.order_by(Article.published_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        articles = result.scalars().all()
        items = [
            {
                "id": a.id,
                "title": a.title,
                "summary": a.summary,
                "cover_image": a.cover_image,
                "category_id": a.category_id,
                "view_count": a.view_count,
                "like_count": a.like_count,
                "status": a.status,
                "published_at": a.published_at,
                "created_at": a.created_at,
            }
            for a in articles
        ]
        return {
            "items": items,
            "total": len(article_ids),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(article_ids) + page_size - 1) // page_size,
        }


async def get_article(article_id: int, user_id: Optional[int] = None) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        # 非公开文章仅作者可见
        if article.status != 1 and (user_id is None or article.user_id != user_id):
            raise ForbiddenException("无权访问此文章")
        return await _build_article_detail(session, article)


async def update_article(user_id: int, article_id: int, data: ArticleUpdate) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Article).where(Article.id == article_id, Article.user_id == user_id)
        )
        article = result.scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")

        if data.title is not None:
            article.title = data.title
        if data.summary is not None:
            article.summary = data.summary
        if data.cover_image is not None:
            article.cover_image = data.cover_image
        if data.category_id is not None:
            article.category_id = data.category_id

        if data.content is not None:
            collection = get_article_contents()
            await collection.update_one(
                {"article_id": article.id},
                {
                    "$set": {
                        "content": data.content,
                        "content_html": markdown_to_html(data.content),
                        "word_count": count_words(data.content),
                        "reading_time": estimate_reading_time(count_words(data.content)),
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

        if data.tags is not None:
            async with session.begin():
                await session.execute(article_tags.delete().where(article_tags.c.article_id == article.id))
                tag_ids = await get_or_create_tags(session, user_id, data.tags)
                for tag_id in tag_ids:
                    await session.execute(
                        article_tags.insert().values(article_id=article.id, tag_id=tag_id)
                    )

        await session.commit()
        await session.refresh(article)
        await cache_invalidate_pattern("cache:articles:*")
        return await _build_article_detail(session, article)


async def delete_article(user_id: int, article_id: int) -> None:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Article).where(Article.id == article_id, Article.user_id == user_id)
        )
        article = result.scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        await session.delete(article)
        await session.commit()
        await cache_invalidate_pattern("cache:articles:*")


async def publish_article(user_id: int, article_id: int) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Article).where(Article.id == article_id, Article.user_id == user_id)
        )
        article = result.scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        if article.status != 0:
            raise APIException(400, "仅草稿状态可发布")

        article.status = 1
        article.published_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(article)
        await cache_invalidate_pattern("cache:articles:*")
        return await _build_article_detail(session, article)


async def unpublish_article(user_id: int, article_id: int) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Article).where(Article.id == article_id, Article.user_id == user_id)
        )
        article = result.scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        if article.status != 1:
            raise APIException(400, "仅已发布状态可下架")

        article.status = 2
        await session.commit()
        await session.refresh(article)
        await cache_invalidate_pattern("cache:articles:*")
        return await _build_article_detail(session, article)


async def like_article(user_id: int, article_id: int, like: bool) -> int:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        article.like_count = max(0, article.like_count + (1 if like else -1))
        await session.commit()
        return article.like_count
