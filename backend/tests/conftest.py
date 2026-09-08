"""pytest 配置：异步支持、httpx 测试客户端与内存假件。"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api import deps as api_deps
from app.core import middleware as core_middleware
from app.services import auth_service, user_service
from tests.fakes import FakeMongo, FakeRedis, FakeSessionFactory


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture
def fake_db():
    return FakeSessionFactory()


@pytest.fixture
def fake_mongo():
    return FakeMongo()


@pytest.fixture
def auth_env(monkeypatch, fake_redis, fake_db):
    """把认证/用户服务、依赖、限流中间件用到的 Redis 与 DB 替换为内存假件。"""
    monkeypatch.setattr(auth_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(auth_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(user_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(user_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(api_deps, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(core_middleware, "get_redis", lambda: fake_redis)
    return fake_redis, fake_db
