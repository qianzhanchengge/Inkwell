"""测试用内存假件：FakeRedis 与 FakeUserStore，隔离真实 MySQL/Redis。"""
from __future__ import annotations

from datetime import datetime


class FakeRedis:
    """内存版异步 Redis，覆盖认证/限流/黑名单所需的命令。"""

    def __init__(self):
        self._store: dict = {}

    async def get(self, key):
        return self._store.get(key)

    async def set(self, key, value, ex=None):
        self._store[key] = value
        return True

    async def delete(self, *keys):
        for k in keys:
            self._store.pop(k, None)
        return len(keys)

    async def incr(self, key):
        cur = int(self._store.get(key, 0)) + 1
        self._store[key] = str(cur)
        return cur

    async def expire(self, key, ttl):
        return True

    async def scan_iter(self, match=None):
        if False:  # 保持 async generator 形态，测试中无需真实迭代
            yield None


def _extract_filter(statement):
    """从 select(Model).where(column == value) 中提取 (列名, 值)。"""
    where = getattr(statement, "whereclause", None)
    col = getattr(where, "left", None)
    name = getattr(col, "key", None) or getattr(col, "name", None)
    right = getattr(where, "right", None)
    value = getattr(right, "value", None)
    return name, value


class FakeSessionFactory:
    """模拟 async_sessionmaker：调用返回异步上下文管理器，enter 得到 FakeSession。"""

    def __init__(self):
        self.users: list = []
        self._next_id = 1

    def __call__(self):
        return _FakeSessionContext(self)

    def find(self, column: str, value):
        for u in self.users:
            if getattr(u, column, None) == value:
                return u
        return None


class _FakeSessionContext:
    def __init__(self, factory: FakeSessionFactory):
        self.factory = factory

    async def __aenter__(self):
        return _FakeSession(self.factory)

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def __init__(self, factory: FakeSessionFactory):
        self.factory = factory

    async def execute(self, statement):
        name, value = _extract_filter(statement)
        return _FakeResult(self.factory.find(name, value))

    def add(self, obj):
        obj.id = self.factory._next_id
        self.factory._next_id += 1
        # 填充数据库侧默认值（SQLAlchemy 的 default 在 flush 时才生效）
        if getattr(obj, "nickname", None) is None:
            obj.nickname = ""
        if getattr(obj, "bio", None) is None:
            obj.bio = ""
        if getattr(obj, "avatar", None) is None:
            obj.avatar = ""
        if getattr(obj, "status", None) is None:
            obj.status = 1
        obj.created_at = datetime.now()
        obj.updated_at = datetime.now()
        self.factory.users.append(obj)
        return obj

    async def commit(self):
        return None

    async def refresh(self, obj):
        return None


class _FakeResult:
    def __init__(self, obj):
        self._obj = obj

    def scalar_one_or_none(self):
        return self._obj
