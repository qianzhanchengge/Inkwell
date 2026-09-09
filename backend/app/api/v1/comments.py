"""评论路由（§5.1）。"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user_id, get_pagination
from app.core.response import success
from app.schemas.comment import CommentCreate
from app.services import comment_service

router = APIRouter(tags=["评论"])


@router.get("/articles/{article_id}/comments")
async def list_comments(
    article_id: int,
    pagination=Depends(get_pagination),
):
    page, page_size = pagination
    return success(await comment_service.list_comments(article_id, page, page_size))


@router.post("/articles/{article_id}/comments")
async def create_comment(
    article_id: int,
    data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
):
    return success(await comment_service.create_comment(user_id, article_id, data))


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id)):
    await comment_service.delete_comment(user_id, comment_id)
    return success()


@router.post("/comments/{comment_id}/like")
async def toggle_comment_like(
    comment_id: int, user_id: int = Depends(get_current_user_id)
):
    return success(await comment_service.toggle_comment_like(user_id, comment_id))
