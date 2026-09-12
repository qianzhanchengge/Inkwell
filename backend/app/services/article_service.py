"""文章业务逻辑（§5.5、§6.3.2 发布流程）。"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select

from app.core.cache import cache_invalidate_pattern
from app.core.exceptions import APIException, ForbiddenException, NotFoundException
from app.database.mongodb import get_article_contents
from app.database.mysql import get_session_factory, reset_auto_increment_if_empty
from app.database.redis import get_redis
from app.models.article import Article, article_tags
from app.models.article_like import ArticleLike
from app.models.category import Category
from app.models.comment import Comment
from app.models.favorite import ArticleFavorite
from app.models.share import ArticleShare
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.services.tag_service import get_or_create_tags
from app.utils.markdown import count_words, estimate_reading_time, markdown_to_html


async def _build_article_detail(session, article: Article) -> dict:
    collection = get_article_contents()
    content_doc = await collection.find_one({"article_id": article.id})
    content = content_doc["content"] if content_doc else ""
    content_html = content_doc["content_html"] if content_doc else ""

    tags = [{"id": t.id, "name": t.name} for t in (article.tags or [])]

    category = None
    if article.category_id:
        cat_result = await session.execute(
            select(Category).where(Category.id == article.category_id)
        )
        cat = cat_result.scalar_one_or_none()
        if cat is not None:
            category = {"id": cat.id, "name": cat.name}

    return {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "content": content,
        "content_html": content_html,
        "cover_image": article.cover_image,
        "category": category,
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

    # 1. 写正文到 MongoDB
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

    # 2. 写元数据到 MySQL（草稿 status=0）+ 标签关联
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

    # 回写 article_id 到 MongoDB
    await collection.update_one({"_id": doc.inserted_id}, {"$set": {"article_id": article.id}})

    await cache_invalidate_pattern("cache:articles:*")
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
        total = (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
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
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
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

        detail = await _build_article_detail(session, article)

        # 已发布文章：实时阅读量计入 Redis Hash（§4.3，可延迟回写 MySQL）
        if article.status == 1:
            try:
                inc = await get_redis().hincrby(
                    f"stat:article:view:{article.id}", "count", 1
                )
                detail["view_count"] = article.view_count + int(inc)
            except Exception:
                # Redis 不可用时降级：仅返回 MySQL 中的累计值
                pass

        # 互动数据聚合（§5.1-5.4）：评论数、分享数、当前用户点赞/收藏状态
        detail["comment_count"] = (
            await session.execute(
                select(func.count()).select_from(
                    select(Comment)
                    .where(Comment.article_id == article_id, Comment.status == 1)
                    .subquery()
                )
            )
        ).scalar_one()
        detail["share_count"] = (
            await session.execute(
                select(func.count()).select_from(
                    select(ArticleShare)
                    .where(ArticleShare.article_id == article_id)
                    .subquery()
                )
            )
        ).scalar_one()
        detail["is_liked"] = False
        detail["is_favorited"] = False
        if user_id is not None:
            liked = (
                await session.execute(
                    select(ArticleLike).where(
                        ArticleLike.article_id == article_id,
                        ArticleLike.user_id == user_id,
                    )
                )
            ).scalar_one_or_none()
            favorited = (
                await session.execute(
                    select(ArticleFavorite).where(
                        ArticleFavorite.article_id == article_id,
                        ArticleFavorite.user_id == user_id,
                    )
                )
            ).scalar_one_or_none()
            detail["is_liked"] = liked is not None
            detail["is_favorited"] = favorited is not None
        return detail


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
                    },
                    "$inc": {"version": 1},
                },
            )

        if data.tags is not None:
            await session.execute(
                article_tags.delete().where(article_tags.c.article_id == article.id)
            )
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

        # 注意：Article.tags 为 lazy="selectin"，ORM 删除主体时会自动清理 article_tags
        # 关联行，不可再手动 DELETE 关联表，否则会抛 StaleDataError。
        await session.delete(article)
        await session.commit()
        await reset_auto_increment_if_empty(session, "articles")

    # 清理 MongoDB 正文
    await get_article_contents().delete_one({"article_id": article_id})
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


async def toggle_like(user_id: int, article_id: int) -> dict:
    """点赞/取消点赞（一人一赞去重，§5.2）。"""
    factory = get_session_factory()
    async with factory() as session:
        article = (
            await session.execute(select(Article).where(Article.id == article_id))
        ).scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        if article.status != 1:
            raise APIException(400, "仅已发布文章可点赞")

        existing = (
            await session.execute(
                select(ArticleLike).where(
                    ArticleLike.article_id == article_id,
                    ArticleLike.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if existing is not None:
            await session.delete(existing)
            article.like_count = max(0, (article.like_count or 0) - 1)
            liked = False
        else:
            session.add(ArticleLike(article_id=article_id, user_id=user_id))
            article.like_count = (article.like_count or 0) + 1
            liked = True

        await session.commit()
        await cache_invalidate_pattern("cache:articles:*")
        return {"liked": liked, "like_count": article.like_count}


async def get_like_status(user_id: int, article_id: int) -> bool:
    factory = get_session_factory()
    async with factory() as session:
        existing = (
            await session.execute(
                select(ArticleLike).where(
                    ArticleLike.article_id == article_id,
                    ArticleLike.user_id == user_id,
                )
            )
        ).scalar_one_or_none()
        return existing is not None


async def toggle_favorite(user_id: int, article_id: int) -> dict:
    """收藏/取消收藏（§5.3）。"""
    factory = get_session_factory()
    async with factory() as session:
        article = (
            await session.execute(select(Article).where(Article.id == article_id))
        ).scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        if article.status != 1:
            raise APIException(400, "仅已发布文章可收藏")

        existing = (
            await session.execute(
                select(ArticleFavorite).where(
                    ArticleFavorite.article_id == article_id,
                    ArticleFavorite.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if existing is not None:
            await session.delete(existing)
            favorited = False
        else:
            session.add(ArticleFavorite(article_id=article_id, user_id=user_id))
            favorited = True

        await session.commit()
        return {"favorited": favorited}


async def list_favorites(user_id: int, page: int, page_size: int) -> dict:
    """我的收藏列表（§5.3）。"""
    factory = get_session_factory()
    async with factory() as session:
        favs = (
            await session.execute(
                select(ArticleFavorite).where(ArticleFavorite.user_id == user_id)
            )
        ).scalars().all()
        article_ids = [f.article_id for f in favs]
        if not article_ids:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
            }

        stmt = select(Article).where(Article.id.in_(article_ids), Article.status == 1)
        total = (
            await session.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar_one()
        result = await session.execute(
            stmt.order_by(Article.published_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
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
            for a in result.scalars().all()
        ]
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


async def record_share(
    user_id: Optional[int], article_id: int, platform: str = "link"
) -> dict:
    """记录一次分享（复制链接，§5.4），返回文章 URL。"""
    factory = get_session_factory()
    async with factory() as session:
        article = (
            await session.execute(select(Article).where(Article.id == article_id))
        ).scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        if article.status != 1:
            raise APIException(400, "仅已发布文章可分享")

        session.add(
            ArticleShare(
                article_id=article_id,
                user_id=user_id,
                platform=platform or "link",
            )
        )
        await session.commit()
    return {
        "shared": True,
        "article_id": article_id,
        "url": f"/blog/articles/{article_id}",
    }
