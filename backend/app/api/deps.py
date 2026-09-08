"""依赖注入：认证与分页。"""
from typing import Optional, Tuple

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.database.redis import get_redis
from app.utils.logger import logger

security = HTTPBearer(auto_error=False)


def _decode_payload(token: str) -> Optional[dict]:
    try:
        return decode_token(token)
    except (JWTError, KeyError, ValueError, TypeError):
        return None


async def _is_blacklisted(jti: Optional[str]) -> bool:
    """检查 jti 是否已入黑名单；Redis 不可用时降级为不拦截。"""
    if not jti:
        return True
    try:
        redis = get_redis()
        return await redis.get(f"token:blacklist:{jti}") is not None
    except Exception:
        logger.warning("黑名单校验降级：Redis 不可用，跳过校验")
        return False


def extract_jti(credentials: Optional[HTTPAuthorizationCredentials]) -> str:
    """从 Bearer 凭据中解析 jti（解析失败返回空串）。"""
    if credentials is None or credentials.credentials is None:
        return ""
    payload = _decode_payload(credentials.credentials)
    return payload.get("jti", "") if payload else ""


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> int:
    """解析 Bearer Token，返回当前用户 ID（必须登录，且 token 有效未拉黑）。"""
    if credentials is None:
        raise UnauthorizedException("未提供认证令牌")
    payload = _decode_payload(credentials.credentials)
    if payload is None:
        raise UnauthorizedException("令牌无效或已过期")
    if payload.get("type") != "access":
        raise UnauthorizedException("令牌类型错误")
    if await _is_blacklisted(payload.get("jti")):
        raise UnauthorizedException("令牌已失效")
    try:
        return int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise UnauthorizedException("令牌无效")


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[int]:
    """可选认证：有有效 Token 返回用户 ID，否则返回 None（公开接口用）。"""
    if credentials is None:
        return None
    payload = _decode_payload(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        return None
    if await _is_blacklisted(payload.get("jti")):
        return None
    try:
        return int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        return None


def get_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> Tuple[int, int]:
    return page, page_size
