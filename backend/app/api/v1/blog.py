"""博客前台聚合路由（§5.5，全部公开）。"""
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_pagination
from app.core.response import success
from app.services import blog_service

router = APIRouter(prefix="/blog", tags=["博客"])


@router.get("/feed")
async def feed(
    sort: str = Query("latest"),
    category_id: int | None = Query(None),
    tag: str | None = Query(None),
    pagination=Depends(get_pagination),
):
    page, page_size = pagination
    return success(await blog_service.feed(page, page_size, sort, category_id, tag))


@router.get("/hot")
async def hot(top_n: int = Query(10, ge=1, le=50)):
    return success(await blog_service.hot(top_n))


@router.get("/categories")
async def category_stats():
    return success(await blog_service.category_stats())


@router.get("/tags")
async def tag_cloud():
    return success(await blog_service.tag_cloud())


@router.get("/archive")
async def archive():
    return success(await blog_service.archive())


@router.get("/related/{article_id}")
async def related(article_id: int, top_n: int = Query(5, ge=1, le=20)):
    return success(await blog_service.related(article_id, top_n))
