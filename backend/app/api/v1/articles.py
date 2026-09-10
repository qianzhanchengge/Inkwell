"""文章路由（§5.5）。

- 管理类接口（增删改/发布/下架/我的列表）→ 工作台 scope
- 博客互动接口（点赞/收藏/分享）→ 博客 scope
- 公开读接口（列表/搜索/详情）→ 无需认证；详情个性化字段接受任一 scope
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_blog_user_id,
    get_current_user_id,
    get_optional_any_user_id,
    get_optional_blog_user_id,
    get_pagination,
)
from app.core.response import success
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["文章"])


@router.get("")
async def list_public_articles(
    pagination=Depends(get_pagination),
    user_id: Optional[int] = Depends(get_optional_any_user_id),
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


@router.get("/favorites")
async def list_favorites(
    pagination=Depends(get_pagination),
    user_id: int = Depends(get_blog_user_id),
):
    page, page_size = pagination
    return success(await article_service.list_favorites(user_id, page, page_size))


@router.get("/search")
async def search_articles(
    keyword: str = Query(..., min_length=1),
    pagination=Depends(get_pagination),
    user_id: Optional[int] = Depends(get_optional_any_user_id),
):
    page, page_size = pagination
    result = await article_service.search_articles(keyword, page, page_size)
    return success(result)


@router.get("/{article_id}")
async def get_article(
    article_id: int, user_id: Optional[int] = Depends(get_optional_any_user_id)
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
async def toggle_like(article_id: int, user_id: int = Depends(get_blog_user_id)):
    return success(await article_service.toggle_like(user_id, article_id))


@router.get("/{article_id}/like")
async def get_like_status(
    article_id: int, user_id: Optional[int] = Depends(get_optional_blog_user_id)
):
    if user_id is None:
        return success({"liked": False})
    return success({"liked": await article_service.get_like_status(user_id, article_id)})


@router.post("/{article_id}/favorite")
async def toggle_favorite(
    article_id: int, user_id: int = Depends(get_blog_user_id)
):
    return success(await article_service.toggle_favorite(user_id, article_id))


@router.post("/{article_id}/share")
async def share_article(
    article_id: int,
    platform: str = Query("link"),
    user_id: Optional[int] = Depends(get_optional_blog_user_id),
):
    return success(await article_service.record_share(user_id, article_id, platform))
