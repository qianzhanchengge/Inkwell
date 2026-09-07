"""文章路由（§5.5）。"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user_id, get_optional_user_id, get_pagination
from app.core.response import success
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["文章"])


@router.get("")
async def list_public_articles(
    pagination=Depends(get_pagination),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    page, page_size = pagination
    result = await article_service.list_articles(None, page, page_size, public_only=True)
    return success(result)


@router.get("/mine")
async def list_my_articles(
    status: Optional[int] = Query(None),
    pagination=Depends(get_pagination),
    user_id: int = Depends(get_current_user_id),
):
    page, page_size = pagination
    result = await article_service.list_articles(user_id, page, page_size, status)
    return success(result)


@router.get("/search")
async def search_articles(
    keyword: str = Query(..., min_length=1),
    pagination=Depends(get_pagination),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    page, page_size = pagination
    result = await article_service.search_articles(keyword, page, page_size)
    return success(result)


@router.get("/{article_id}")
async def get_article(
    article_id: int, user_id: Optional[int] = Depends(get_optional_user_id)
):
    return success(await article_service.get_article(article_id, user_id))


@router.post("")
async def create_article(data: ArticleCreate, user_id: int = Depends(get_current_user_id)):
    return success(await article_service.create_article(user_id, data))


@router.put("/{article_id}")
async def update_article(
    article_id: int, data: ArticleUpdate, user_id: int = Depends(get_current_user_id)
):
    return success(await article_service.update_article(user_id, article_id, data))


@router.delete("/{article_id}")
async def delete_article(article_id: int, user_id: int = Depends(get_current_user_id)):
    await article_service.delete_article(user_id, article_id)
    return success()


@router.post("/{article_id}/publish")
async def publish_article(article_id: int, user_id: int = Depends(get_current_user_id)):
    return success(await article_service.publish_article(user_id, article_id))


@router.post("/{article_id}/unpublish")
async def unpublish_article(article_id: int, user_id: int = Depends(get_current_user_id)):
    return success(await article_service.unpublish_article(user_id, article_id))


@router.post("/{article_id}/like")
async def like_article(
    article_id: int,
    like: bool = Query(True),
    user_id: int = Depends(get_current_user_id),
):
    count = await article_service.like_article(user_id, article_id, like)
    return success({"like_count": count})
