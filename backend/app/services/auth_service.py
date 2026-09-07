"""认证业务逻辑：注册 / 登录 / 登出。"""
from sqlalchemy import select

from app.config import settings
from app.core.exceptions import ConflictException, ForbiddenException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    new_jti,
    verify_password,
)
from app.database.mysql import get_session_factory
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister


async def register(data: UserRegister) -> User:
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
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def login(data: UserLogin) -> dict:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(User).where(User.username == data.username))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("用户名或密码错误")
        if user.status != 1:
            raise ForbiddenException("账号已被禁用")

        jti = new_jti()
        access_token = create_access_token(user.id, user.username, jti)
        refresh_token = create_refresh_token(user.id, user.username, jti)

        redis = get_redis()
        await redis.set(
            f"user:token:{user.id}",
            jti,
            ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }


async def logout(user_id: int, jti: str) -> None:
    """登出：将 jti 加入黑名单，并清除会话 Token。"""
    redis = get_redis()
    await redis.set(f"token:blacklist:{jti}", "1", ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    await redis.delete(f"user:token:{user_id}")
