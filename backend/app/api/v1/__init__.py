"""API v1 路由聚合。"""
from fastapi import APIRouter

from app.api.v1 import (
    articles,
    auth,
    categories,
    notes,
    stats,
    tags,
    upload,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(notes.router)
api_router.include_router(articles.router)
api_router.include_router(categories.router)
api_router.include_router(tags.router)
api_router.include_router(stats.router)
api_router.include_router(upload.router)
