"""MySQL 异步连接（SQLAlchemy 2.0 + aiomysql）。

连接采用惰性初始化：只有真正执行数据库操作时才建立连接，
因此 ``import app.main`` 不依赖运行中的 MySQL。
"""
from typing import AsyncGenerator
from urllib.parse import quote_plus

from sqlalchemy.dialects.mysql import aiomysql as _aiomysql
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class AioMySQLDialect(_aiomysql.MySQLDialect_aiomysql):
    """修复 SQLAlchemy 2.0.x + PyMySQL 1.2.0 下 pool_pre_ping 的兼容问题。

    PyMySQL 1.2.0 把 Connection.ping 的默认参数改为 reconnect=False，
    SQLAlchemy 的 _send_false_to_ping 据此认为可无参调用 ping()；但
    aiomysql 异步包装层的 ping() 必须显式传参（且断言 reconnect=False），
    无参调用会抛 TypeError。强制返回 True，使 do_ping 显式调用 ping(False)。
    """

    @property
    def _send_false_to_ping(self) -> bool:
        return True


class Base(DeclarativeBase):
    """所有 ORM 模型的声明式基类。"""


_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_engine():
    global _engine
    if _engine is None:
        url = (
            f"mysql+aiomysql://{quote_plus(settings.MYSQL_USER)}:"
            f"{quote_plus(settings.MYSQL_PASSWORD)}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )
        _engine = create_async_engine(
            url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            dialect=AioMySQLDialect(),
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=_get_engine(), expire_on_commit=False
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供一个数据库会话。"""
    factory = get_session_factory()
    async with factory() as session:
        yield session
