"""中间件：请求日志与接口限流（§6.2 / §12.3）。"""
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.redis import get_redis
from app.utils.logger import logger

# 需要限流的路径：路径 -> (窗口秒数, 最大次数)
RATE_LIMIT_RULES = {
    "/auth/login": (60, 5),
}


class RequestLogMiddleware(BaseHTTPMiddleware):
    """记录每个请求的方法、路径、状态码与耗时。"""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """基于 Redis 的 IP+路径计数器限流，Redis 不可用时降级为放行。"""

    async def dispatch(self, request: Request, call_next):
        rule = RATE_LIMIT_RULES.get(request.url.path)
        if rule is not None:
            window, limit = rule
            ip = request.client.host if request.client else "unknown"
            key = f"rate:limit:{ip}:{request.url.path}"
            try:
                redis = get_redis()
                count = await redis.incr(key)
                if count == 1:
                    await redis.expire(key, window)
                if count > limit:
                    return JSONResponse(
                        status_code=429,
                        content={"code": 429, "message": "请求过于频繁，请稍后再试", "data": None},
                    )
            except Exception:  # Redis 不可用时放行，避免误伤
                logger.warning("限流降级：Redis 不可用，跳过限流")
        return await call_next(request)
