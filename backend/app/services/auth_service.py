"""认证业务逻辑：注册 / 登录 / 登出 / 刷新。

认证拆分为两套**独立会话**（scope）：

- ``workbench``：工作台（仅 ``user_type=1`` 可登录）
- ``blog``：博客前台（``user_type=1`` 或 ``2`` 均可登录）

两套会话的 JWT ``scope`` 载荷与 Redis 会话键均独立，互不影响
（工作台登录/登出不会改变博客登录态，反之亦然）。
"""
from sqlalchemy import select

from app.config import settings
from app.core.exceptions import ConflictException, ForbiddenException, UnauthorizedException
from app.core.security import (
    SCOPE_BLOG,
    SCOPE_WORKBENCH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    new_jti,
    token_remaining_ttl,
    token_scope,
    verify_password,
)
from app.database.mysql import get_session_factory
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister

USER_TYPE_WORKBENCH = 1
USER_TYPE_BLOG = 2

# 各会话允许登录的用户类型（工作台拒绝博客用户）
SCOPE_ALLOWED_TYPES = {
    SCOPE_WORKBENCH: (USER_TYPE_WORKBENCH,),
    SCOPE_BLOG: (USER_TYPE_WORKBENCH, USER_TYPE_BLOG),
}


def _session_key(scope: str, user_id: int) -> str:
    """按会话作用域返回 Redis 会话键（两套会话互不覆盖）。"""
    if scope == SCOPE_BLOG:
        return f"blog:user:token:{user_id}"
    return f"user:token:{user_id}"


def _effective_type(user: User) -> int:
    """取用户类型；历史数据为 NULL 时视为工作台用户。"""
    return user.user_type or USER_TYPE_WORKBENCH


async def register(data: UserRegister, user_type: int = USER_TYPE_WORKBENCH) -> User:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none() is not None:
            raise ConflictException("用户名已存在")

        result = await session.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none() is not None:
            raise ConflictException("邮箱已被注册")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            nickname=data.nickname or "",
            user_type=user_type,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def login(data: UserLogin, scope: str = SCOPE_WORKBENCH) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(User).where(User.username == data.username))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("用户名或密码错误")
        if user.status != 1:
            raise ForbiddenException("账号已被禁用")

        allowed = SCOPE_ALLOWED_TYPES.get(scope, (USER_TYPE_WORKBENCH,))
        if _effective_type(user) not in allowed:
            if scope == SCOPE_WORKBENCH:
                raise ForbiddenException("该账号为博客用户，无法登录工作台")
            raise ForbiddenException("该账号类型不允许登录")

        jti = new_jti()
        access_token = create_access_token(user.id, user.username, jti, scope)
        refresh_token = create_refresh_token(user.id, user.username, jti, scope)

        redis = get_redis()
        await redis.set(
            _session_key(scope, user.id),
            jti,
            ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }


async def logout(
    user_id: int, jti: str, token: str = "", scope: str = SCOPE_WORKBENCH
) -> None:
    """登出：将 jti 加入黑名单（TTL 对齐 token 剩余时间），并清除本会话的 Token。"""
    redis = get_redis()
    ttl = token_remaining_ttl(token) if token else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    if jti:
        await redis.set(f"token:blacklist:{jti}", "1", ex=ttl)
    await redis.delete(_session_key(scope, user_id))


async def refresh(refresh_token: str, expected_scope: str | None = None) -> dict:
    """刷新 Token：校验 refresh token 有效且未拉黑，按原 scope 签发新的 access/refresh。"""
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise UnauthorizedException("令牌无效或已过期")

    if payload.get("type") != "refresh":
        raise UnauthorizedException("令牌类型错误")

    scope = token_scope(payload)
    if expected_scope is not None and scope != expected_scope:
        raise UnauthorizedException("令牌作用域不匹配")

    jti = payload.get("jti")
    redis = get_redis()
    if jti and await redis.get(f"token:blacklist:{jti}") is not None:
        raise UnauthorizedException("令牌已失效")

    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise UnauthorizedException("令牌无效")

    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedException("用户不存在")
    if user.status != 1:
        raise ForbiddenException("账号已被禁用")

    allowed = SCOPE_ALLOWED_TYPES.get(scope, (USER_TYPE_WORKBENCH,))
    if _effective_type(user) not in allowed:
        raise ForbiddenException("该账号类型不允许该会话")

    fresh_jti = new_jti()
    access_token = create_access_token(user.id, user.username, fresh_jti, scope)
    new_refresh_token = create_refresh_token(user.id, user.username, fresh_jti, scope)
    await redis.set(
        _session_key(scope, user.id),
        fresh_jti,
        ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
