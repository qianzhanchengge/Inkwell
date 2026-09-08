"""用户业务逻辑。"""
from sqlalchemy import select

from app.config import settings
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.core.security import hash_password, token_remaining_ttl, verify_password
from app.database.mysql import get_session_factory
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.user import PasswordUpdate, UserProfileUpdate


async def get_user(user_id: int) -> User:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundException("用户不存在")
        return user


async def update_profile(user_id: int, data: UserProfileUpdate) -> User:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundException("用户不存在")

        if data.nickname is not None:
            user.nickname = data.nickname
        if data.bio is not None:
            user.bio = data.bio
        if data.avatar is not None:
            user.avatar = data.avatar

        await session.commit()
        await session.refresh(user)
        return user


async def change_password(
    user_id: int, data: PasswordUpdate, jti: str = "", token: str = ""
) -> None:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundException("用户不存在")
        if not verify_password(data.old_password, user.password_hash):
            raise UnauthorizedException("原密码错误")

        user.password_hash = hash_password(data.new_password)
        await session.commit()

    # 修改密码后使旧会话失效（拉黑当前 jti 并清除会话 Token）
    if jti:
        redis = get_redis()
        ttl = token_remaining_ttl(token) if token else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        await redis.set(f"token:blacklist:{jti}", "1", ex=ttl)
        await redis.delete(f"user:token:{user_id}")
