"""测试用内存假件：FakeRedis、FakeSessionFactory、FakeMongo，隔离真实 MySQL/Redis/MongoDB。

FakeSessionFactory 提供一个内存关系型存储，能解释本项目中 services 层用到的
select / count / insert / delete / update 语句形状（覆盖 auth / user / note /
category / tag 各服务），供 API 级测试使用，不依赖真实数据库。
"""
from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.sql.dml import Delete, Insert, Update
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList

from app.database.mysql import Base
from app.models.article import Article, article_tags
from app.models.category import Category
from app.models.note import Note, note_tags
from app.models.tag import Tag
from app.models.user import User

_MODEL_BY_TABLE = {
    "users": User,
    "notes": Note,
    "articles": Article,
    "categories": Category,
    "tags": Tag,
}


class FakeRedis:
    """内存版异步 Redis，覆盖认证/限流/黑名单/缓存/统计所需的命令。"""

    def __init__(self):
        self._store: dict = {}
        self._hashes: dict = {}

    async def get(self, key):
        return self._store.get(key)

    async def hgetall(self, key):
        return dict(self._hashes.get(key, {}))

    async def hset(self, key, field, value):
        self._hashes.setdefault(key, {})[field] = value
        return 1

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

    async def hincrby(self, name, key, amount=1):
        h = self._hashes.setdefault(name, {})
        h[key] = int(h.get(key, 0)) + amount
        return h[key]

    async def expire(self, key, ttl):
        return True

    async def scan_iter(self, match=None):
        if False:  # 保持 async generator 形态，测试中无需真实迭代
            yield None


# --------------------------------------------------------------------------- #
# 内存关系型存储
# --------------------------------------------------------------------------- #

def _right_value(right):
    """取 where 子句右值（可能是 BindParameter、字面量或列表）。"""
    if hasattr(right, "value"):
        return right.value
    return right


def _matches(obj, where) -> bool:
    """按 SQLAlchemy whereclause 判断 obj 是否命中。"""
    if where is None:
        return True
    if isinstance(where, BooleanClauseList):
        return all(_matches(obj, c) for c in where.clauses)
    if isinstance(where, BinaryExpression):
        left = where.left
        right = where.right
        col = getattr(left, "key", None) or getattr(left, "name", None)
        actual = getattr(obj, col, None)
        val = _right_value(right)
        opname = getattr(where.operator, "__name__", "")
        if opname == "eq":
            return actual == val
        if opname in ("like_op", "ilike_op"):
            regex = "^" + re.escape(str(val)).replace("%", ".*") + "$"
            return bool(re.match(regex, str(actual)))
        if opname == "in_op":
            return actual in list(val or [])
        if opname in ("is_", "is_not"):
            return (actual is val) if opname == "is_" else (actual is not val)
        if opname == "ge":
            return actual >= val
        if opname == "le":
            return actual <= val
        if opname == "gt":
            return actual > val
        if opname == "lt":
            return actual < val
        if opname == "ne":
            return actual != val
        return actual == val
    return True


def _model_of(statement):
    """从 select 语句的 column_descriptions 推断目标 ORM 模型。"""
    for desc in statement.column_descriptions:
        ent = desc.get("entity") or desc.get("type")
        if isinstance(ent, type) and issubclass(ent, Base):
            return ent
    return None


def _is_count(statement) -> bool:
    raw = getattr(statement, "_raw_columns", None)
    if raw:
        first = raw[0]
        if getattr(first, "name", None) == "count":
            return True
    return False


def _dml_values(statement) -> dict:
    """提取 Insert/Update 的 .values(...) 参数（键规范化字符串，值解包 BindParameter）。"""
    vals = getattr(statement, "_values", None)
    if isinstance(vals, dict):
        raw = vals
    elif isinstance(vals, (list, tuple)) and vals and isinstance(vals[0], dict):
        raw = vals[0]
    else:
        try:
            raw = statement.compile().params
        except Exception:
            return {}
    out = {}
    for k, v in raw.items():
        key = getattr(k, "key", None) or getattr(k, "name", None) or str(k)
        out[key] = _right_value(v)
    return out


class FakeSessionFactory:
    """模拟 async_sessionmaker：返回异步上下文管理器，enter 得到共享内存库的 FakeSession。"""

    def __init__(self):
        self._rows: dict = {}
        self._next_id = 1
        # 多对多关系：note_tags / article_tags 的 (a_id, tag_id) 集合
        self.note_tags_rel: set = set()
        self.article_tags_rel: set = set()

    def __call__(self):
        return _FakeSessionContext(self)

    def rows(self, model):
        return self._rows.setdefault(model, [])

    def next_id(self):
        nid = self._next_id
        self._next_id += 1
        return nid


class _FakeSessionContext:
    def __init__(self, factory: FakeSessionFactory):
        self.factory = factory

    async def __aenter__(self):
        return _FakeSession(self.factory)

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeBegin:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def __init__(self, factory: FakeSessionFactory):
        self.factory = factory

    # -- 生命周期 ---------------------------------------------------------- #
    def begin(self):
        return _FakeBegin()

    async def commit(self):
        return None

    async def flush(self):
        return None

    async def refresh(self, obj):
        self._hydrate(obj)
        return None

    def add(self, obj):
        self._set_defaults(obj)
        if getattr(obj, "id", None) is None:
            obj.id = self.factory.next_id()
        lst = self.factory.rows(type(obj))
        if obj not in lst:
            lst.append(obj)
        return obj

    async def delete(self, obj):
        lst = self.factory.rows(type(obj))
        if obj in lst:
            lst.remove(obj)
        if isinstance(obj, Tag):
            self.factory.note_tags_rel = {
                (a, b) for (a, b) in self.factory.note_tags_rel if b != obj.id
            }
            self.factory.article_tags_rel = {
                (a, b) for (a, b) in self.factory.article_tags_rel if b != obj.id
            }

    # -- 语句执行 ---------------------------------------------------------- #
    async def execute(self, statement):
        if isinstance(statement, Insert):
            self._handle_insert(statement)
            return _FakeResult([], self)
        if isinstance(statement, Delete):
            self._handle_delete(statement)
            return _FakeResult([], self)
        if isinstance(statement, Update):
            self._handle_update(statement)
            return _FakeResult([], self)
        if _is_count(statement):
            return _FakeResult([self._handle_count(statement)], self)
        rows = self._handle_select(statement)
        return _FakeResult(rows, self)

    # -- 内部 -------------------------------------------------------------- #
    def _set_defaults(self, obj):
        now = datetime.now()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = now
        if isinstance(obj, User):
            for f in ("nickname", "bio", "avatar"):
                if getattr(obj, f, None) is None:
                    setattr(obj, f, "")
            if getattr(obj, "status", None) is None:
                obj.status = 1
        elif isinstance(obj, Note):
            if getattr(obj, "status", None) is None:
                obj.status = 1
            if getattr(obj, "is_pinned", None) is None:
                obj.is_pinned = 0
        elif isinstance(obj, Article):
            if getattr(obj, "status", None) is None:
                obj.status = 0
            if getattr(obj, "view_count", None) is None:
                obj.view_count = 0
            if getattr(obj, "like_count", None) is None:
                obj.like_count = 0
            if getattr(obj, "summary", None) is None:
                obj.summary = ""
            if getattr(obj, "cover_image", None) is None:
                obj.cover_image = ""
        elif isinstance(obj, Category):
            if getattr(obj, "sort_order", None) is None:
                obj.sort_order = 0

    def _hydrate(self, obj):
        """把关系字段（如 note.tags / article.tags）从多对多关系集合填充为普通列表。"""
        if isinstance(obj, Note):
            tag_ids = sorted({t for (n, t) in self.factory.note_tags_rel if n == obj.id})
            obj.tags = [t for t in self.factory.rows(Tag) if t.id in tag_ids]
        if isinstance(obj, Article):
            tag_ids = sorted({t for (a, t) in self.factory.article_tags_rel if a == obj.id})
            obj.tags = [t for t in self.factory.rows(Tag) if t.id in tag_ids]
        return obj

    def _handle_select(self, statement):
        model = _model_of(statement)
        if model is None:
            return []
        rows = [r for r in self.factory.rows(model) if _matches(r, statement.whereclause)]
        offset = getattr(statement, "_offset", 0) or 0
        limit = getattr(statement, "_limit", None)
        if limit is not None:
            rows = rows[offset : offset + limit]
        else:
            rows = rows[offset:]
        return list(rows)

    def _handle_count(self, statement):
        where = statement.whereclause
        model = _model_of(statement)
        if model is None:
            for from_obj in statement.get_final_froms():
                inner = getattr(from_obj, "element", None)
                if inner is not None:
                    m = _model_of(inner)
                    if m is not None:
                        model = m
                        where = getattr(inner, "whereclause", where)
                        break
                name = getattr(from_obj, "name", None)
                m = _MODEL_BY_TABLE.get(name)
                if m is not None:
                    model = m
                    break
        if model is None:
            return 0
        return len([r for r in self.factory.rows(model) if _matches(r, where)])

    def _handle_insert(self, statement):
        tname = statement.table.name
        vals = _dml_values(statement)
        if tname == "note_tags":
            self.factory.note_tags_rel.add((vals.get("note_id"), vals.get("tag_id")))
        elif tname == "article_tags":
            self.factory.article_tags_rel.add((vals.get("article_id"), vals.get("tag_id")))

    def _handle_delete(self, statement):
        tname = statement.table.name
        if tname not in ("note_tags", "article_tags"):
            return
        where = statement.whereclause
        col = getattr(where.left, "key", None) or getattr(where.left, "name", None)
        val = _right_value(where.right)
        if tname == "note_tags":
            self.factory.note_tags_rel = {
                (a, b) for (a, b) in self.factory.note_tags_rel
                if not ((col == "note_id" and a == val) or (col == "tag_id" and b == val))
            }
        else:
            self.factory.article_tags_rel = {
                (a, b) for (a, b) in self.factory.article_tags_rel
                if not ((col == "article_id" and a == val) or (col == "tag_id" and b == val))
            }

    def _handle_update(self, statement):
        model = _MODEL_BY_TABLE.get(statement.table.name)
        if model is None:
            return
        rows = [r for r in self.factory.rows(model) if _matches(r, statement.whereclause)]
        vals = _dml_values(statement)
        for r in rows:
            for k, v in vals.items():
                setattr(r, k, v)


class _FakeResult:
    def __init__(self, rows, session=None):
        self._rows = rows
        self._session = session

    def _hydrated(self):
        if self._session is not None:
            return [self._session._hydrate(r) for r in self._rows]
        return self._rows

    def scalar_one_or_none(self):
        rows = self._hydrated()
        return rows[0] if rows else None

    def scalar_one(self):
        rows = self._hydrated()
        if not rows:
            raise Exception("No result found")
        return rows[0]

    def scalars(self):
        return _FakeScalars(self._hydrated())

    def all(self):
        return self._hydrated()


class _FakeScalars:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None


# --------------------------------------------------------------------------- #
# 内存 MongoDB
# --------------------------------------------------------------------------- #

class FakeCollection:
    def __init__(self, name):
        self.name = name
        self._docs: list = []
        self._next_id = 1

    async def insert_one(self, doc):
        doc = dict(doc)
        doc["_id"] = self._next_id
        self._next_id += 1
        self._docs.append(doc)
        return _FakeInsertResult(doc["_id"])

    async def find_one(self, query):
        for d in self._docs:
            if _doc_matches(d, query):
                return dict(d)
        return None

    async def update_one(self, query, update):
        for d in self._docs:
            if _doc_matches(d, query):
                if "$set" in update:
                    d.update(update["$set"])
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        d[k] = d.get(k, 0) + v
                return _FakeUpdateResult(1)
        return _FakeUpdateResult(0)

    async def delete_many(self, query):
        before = len(self._docs)
        self._docs = [d for d in self._docs if not _doc_matches(d, query)]
        return _FakeDeleteResult(before - len(self._docs))

    async def delete_one(self, query):
        before = len(self._docs)
        self._docs = [d for d in self._docs if not _doc_matches(d, query)]
        return _FakeDeleteResult(before - len(self._docs))

    def find(self, query):
        return _FakeCursor([dict(d) for d in self._docs if _doc_matches(d, query)])


def _doc_matches(doc, query) -> bool:
    for k, v in (query or {}).items():
        if isinstance(v, dict) and "$regex" in v:
            pattern = v["$regex"]
            flags = re.IGNORECASE if v.get("$options", "").find("i") >= 0 else 0
            if not re.search(pattern, str(doc.get(k, "")), flags):
                return False
        elif doc.get(k) != v:
            return False
    return True


class _FakeInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class _FakeUpdateResult:
    def __init__(self, matched):
        self.modified_count = matched
        self.matched_count = matched


class _FakeDeleteResult:
    def __init__(self, deleted):
        self.deleted_count = deleted


class _FakeCursor:
    def __init__(self, docs):
        self._docs = iter(docs)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._docs)
        except StopIteration:
            raise StopAsyncIteration


class FakeMongo:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        return self.collections.setdefault(name, FakeCollection(name))
