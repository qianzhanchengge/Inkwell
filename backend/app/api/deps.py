"""依赖注入：认证与分页。"""
from typing import Optional, Tuple

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token

security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> int:
    """解析 Bearer Token，返回当前用户 ID（必须登录）。"""
    if credentials is None:
        raise UnauthorizedException("未提供认证令牌")
    try:
        payload = decode_token(credentials.credentials)
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError, TypeError):
        raise UnauthorizedException("令牌无效或已过期")


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[int]:
    """可选认证：有 Token 返回用户 ID，无/无效则返回 None（公开接口用）。"""
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError, TypeError):
        return None


def get_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> Tuple[int, int]:
    return page, page_size
