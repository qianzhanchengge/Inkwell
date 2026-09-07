"""Redis 异步连接（redis-py asyncio）。

Redis 客户端惰性连接：首次执行命令时才真正连接，
因此 ``import app.main`` 不依赖运行中的 Redis。
"""
from redis.asyncio import Redis

from app.config import settings

_client: Redis | None = None


def get_redis() -> Redis:
    global _client
    if _client is None:
        _client = Redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
    return _client
