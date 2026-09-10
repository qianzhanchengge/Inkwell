"""依赖注入：认证（工作台 / 博客双 scope）与分页。

Token 作用域：
- ``workbench``：工作台管理接口（笔记/文章管理、分类、标签、统计、个人设置等）
- ``blog``：博客前台互动接口（点赞、收藏、分享、评论）

只读个性化字段（如文章详情的 ``is_liked``/``is_favorited``）接受任一 scope。
旧 Token 无 ``scope`` 载荷时视为 ``workbench``（向后兼容）。
"""
from typing import Optional, Tuple

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.exceptions import UnauthorizedException
from app.core.security import SCOPE_BLOG, SCOPE_WORKBENCH, decode_token, token_scope
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


def _user_id_of(payload: dict) -> int:
    try:
        return int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise UnauthorizedException("令牌无效")


async def _require(credentials: Optional[HTTPAuthorizationCredentials], scope: str) -> int:
    """必须登录且 Token scope 匹配，返回用户 ID。"""
    if credentials is None:
        raise UnauthorizedException("未提供认证令牌")
    payload = _decode_payload(credentials.credentials)
    if payload is None:
        raise UnauthorizedException("令牌无效或已过期")
    if payload.get("type") != "access":
        raise UnauthorizedException("令牌类型错误")
    if await _is_blacklisted(payload.get("jti")):
        raise UnauthorizedException("令牌已失效")
    if token_scope(payload) != scope:
        raise UnauthorizedException("令牌作用域不匹配，请重新登录")
    return _user_id_of(payload)


async def _optional(
    credentials: Optional[HTTPAuthorizationCredentials], scopes: Tuple[str, ...]
) -> Optional[int]:
    """可选认证：Token 有效且 scope 在允许集合内返回用户 ID，否则 None。"""
    if credentials is None:
        return None
    payload = _decode_payload(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        return None
    if await _is_blacklisted(payload.get("jti")):
        return None
    if token_scope(payload) not in scopes:
        return None
    try:
        return int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        return None


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> int:
    """工作台身份：必须登录且 scope=workbench。"""
    return await _require(credentials, SCOPE_WORKBENCH)


async def get_blog_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> int:
    """博客身份：必须登录且 scope=blog。"""
    return await _require(credentials, SCOPE_BLOG)


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[int]:
    """工作台可选身份：仅接受 scope=workbench，否则 None。"""
    return await _optional(credentials, (SCOPE_WORKBENCH,))


async def get_optional_blog_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[int]:
    """博客可选身份：仅接受 scope=blog，否则 None（游客）。"""
    return await _optional(credentials, (SCOPE_BLOG,))


async def get_optional_any_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[int]:
    """可选身份：接受任一 scope，用于只读个性化字段。"""
    return await _optional(credentials, (SCOPE_WORKBENCH, SCOPE_BLOG))


def get_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> Tuple[int, int]:
    return page, page_size
