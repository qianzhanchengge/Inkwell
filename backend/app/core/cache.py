"""Redis 缓存工具：缓存装饰器与主动失效（§6.2.3）。"""
import json
from typing import Any, Callable, Optional

from app.database.redis import get_redis


async def cache_get(key: str) -> Optional[Any]:
    raw = await get_redis().get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    await get_redis().set(key, json.dumps(value, ensure_ascii=False, default=str), ex=ttl)


async def cache_delete(key: str) -> None:
    await get_redis().delete(key)


async def cache_invalidate_pattern(pattern: str) -> None:
    """删除匹配 pattern 的键（如 cache:notes:list:1:*）。"""
    redis = get_redis()
    async for key in redis.scan_iter(match=pattern):
        await redis.delete(key)


def cached(ttl: int = 300, key_pattern: Optional[str] = None) -> Callable:
    """缓存装饰器：缓存异步函数返回值到 Redis。

    key_pattern 支持 {name} 占位符，从 kwargs 或 args 中取值。
    """

    def decorator(func: Callable) -> Callable:
        import functools

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if key_pattern is None:
                return await func(*args, **kwargs)

            try:
                key = key_pattern.format(**kwargs, **dict(zip(func.__code__.co_varnames, args)))
            except (KeyError, IndexError, AttributeError):
                key = None

            if key:
                cached_value = await cache_get(key)
                if cached_value is not None:
                    return cached_value

            result = await func(*args, **kwargs)

            if key:
                await cache_set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator
