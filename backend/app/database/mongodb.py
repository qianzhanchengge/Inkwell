"""MongoDB 异步连接（Motor）。

Motor 的 AsyncIOMotorClient 惰性连接：首次真正读写时才建立连接，
因此 ``import app.main`` 不依赖运行中的 MongoDB。
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
    if _db is None:
        _db = _client[settings.MONGODB_DB]
    return _db


def get_note_contents():
    return get_db()["note_contents"]


def get_article_contents():
    return get_db()["article_contents"]
