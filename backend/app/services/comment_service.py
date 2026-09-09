"""评论业务逻辑（§5.1、§8.3）。"""
from typing import Optional

from sqlalchemy import func, select

from app.core.exceptions import (
    APIException,
    ForbiddenException,
    NotFoundException,
)
from app.database.mysql import get_session_factory
from app.models.article import Article
from app.models.comment import Comment, CommentLike
from app.models.user import User
from app.schemas.comment import CommentCreate


async def _get_user_map(session, user_ids) -> dict:
    """批量取用户昵称/头像，避免 N+1。"""
    ids = sorted({uid for uid in user_ids if uid})
    if not ids:
        return {}
    result = await session.execute(select(User).where(User.id.in_(ids)))
    return {
        u.id: {"nickname": u.nickname or u.username, "avatar": u.avatar or ""}
        for u in result.scalars().all()
    }


def _serialize_comment(comment: Comment, user_map: dict) -> dict:
    author = user_map.get(comment.user_id, {})
    reply_to = user_map.get(comment.reply_to_user_id) if comment.reply_to_user_id else None
    return {
        "id": comment.id,
        "article_id": comment.article_id,
        "user_id": comment.user_id,
        "author_nickname": author.get("nickname", ""),
        "author_avatar": author.get("avatar", ""),
        "parent_id": comment.parent_id,
        "reply_to_user_id": comment.reply_to_user_id,
        "reply_to_nickname": (reply_to or {}).get("nickname"),
        "content": comment.content,
        "like_count": comment.like_count or 0,
        "created_at": comment.created_at,
    }


async def list_comments(article_id: int, page: int, page_size: int) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        article = (
            await session.execute(select(Article).where(Article.id == article_id))
        ).scalar_one_or_none()
        if article is None or article.status != 1:
            raise NotFoundException("文章不存在")

        stmt = (
            select(Comment)
            .where(Comment.article_id == article_id, Comment.status == 1)
            .order_by(Comment.created_at.asc(), Comment.id.asc())
        )
        total = (
            await session.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar_one()
        result = await session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        comments = result.scalars().all()

        user_ids = {c.user_id for c in comments}
        user_ids |= {c.reply_to_user_id for c in comments if c.reply_to_user_id}
        user_map = await _get_user_map(session, user_ids)

        items = [_serialize_comment(c, user_map) for c in comments]
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


async def create_comment(user_id: int, article_id: int, data: CommentCreate) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        article = (
            await session.execute(select(Article).where(Article.id == article_id))
        ).scalar_one_or_none()
        if article is None:
            raise NotFoundException("文章不存在")
        if article.status != 1:
            raise APIException(400, "仅已发布文章可评论")

        if data.parent_id is not None:
            parent = (
                await session.execute(
                    select(Comment).where(
                        Comment.id == data.parent_id,
                        Comment.article_id == article_id,
                        Comment.status == 1,
                    )
                )
            ).scalar_one_or_none()
            if parent is None:
                raise NotFoundException("父评论不存在")

        comment = Comment(
            article_id=article_id,
            user_id=user_id,
            parent_id=data.parent_id,
            reply_to_user_id=data.reply_to_user_id,
            content=data.content,
            like_count=0,
            status=1,
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)

        user_map = await _get_user_map(session, {user_id, data.reply_to_user_id})
        return _serialize_comment(comment, user_map)


async def delete_comment(user_id: int, comment_id: int) -> None:
    factory = get_session_factory()
    async with factory() as session:
        comment = (
            await session.execute(select(Comment).where(Comment.id == comment_id))
        ).scalar_one_or_none()
        if comment is None:
            raise NotFoundException("评论不存在")

        # 仅评论者本人或文章作者可删
        if comment.user_id != user_id:
            article = (
                await session.execute(select(Article).where(Article.id == comment.article_id))
            ).scalar_one_or_none()
            if article is None or article.user_id != user_id:
                raise ForbiddenException("无权删除此评论")

        comment.status = 0  # 软删除
        await session.commit()


async def toggle_comment_like(user_id: int, comment_id: int) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        comment = (
            await session.execute(select(Comment).where(Comment.id == comment_id))
        ).scalar_one_or_none()
        if comment is None or comment.status != 1:
            raise NotFoundException("评论不存在")

        existing = (
            await session.execute(
                select(CommentLike).where(
                    CommentLike.comment_id == comment_id,
                    CommentLike.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if existing is not None:
            await session.delete(existing)
            comment.like_count = max(0, (comment.like_count or 0) - 1)
            liked = False
        else:
            session.add(CommentLike(comment_id=comment_id, user_id=user_id))
            comment.like_count = (comment.like_count or 0) + 1
            liked = True

        await session.commit()
        return {"liked": liked, "like_count": comment.like_count}
