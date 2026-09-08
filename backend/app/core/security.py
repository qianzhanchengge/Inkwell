"""认证与安全：密码哈希（bcrypt）与 JWT 编解码（§6.2.2）。"""
import time
import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def new_jti() -> str:
    """生成 Token 唯一标识（用于黑名单 / 单设备登录）。"""
    return uuid.uuid4().hex


def _create_token(
    subject: str,
    username: str,
    jti: str,
    expires_delta: timedelta,
    token_type: str,
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": subject,
        "username": username,
        "jti": jti,
        "type": token_type,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: int, username: str, jti: str) -> str:
    return _create_token(
        str(user_id),
        username,
        jti,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(user_id: int, username: str, jti: str) -> str:
    return _create_token(
        str(user_id),
        username,
        jti,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def token_remaining_ttl(token: str) -> int:
    """计算 Token 剩余有效秒数，用于黑名单 TTL（对齐 Token 过期时间）。

    无法解析或已过期时回退为默认 access token 生命周期（保守拉黑）。
    """
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp:
            remaining = int(exp - time.time())
            if remaining > 0:
                return remaining
    except Exception:
        pass
    return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
