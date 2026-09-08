"""统计接口测试（Phase 5，基于内存假件，不依赖真实数据库）。"""
from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from app.models.article import Article
from app.models.note import Note


@pytest.fixture
def stats_env(monkeypatch, fake_redis, fake_db, fake_mongo):
    """把认证/用户/统计服务用到的 Redis/DB/Mongo 替换为内存假件。"""
    import app.api.deps as api_deps
    import app.core.middleware as core_middleware
    import app.services.auth_service as auth_service
    import app.services.stats_service as stats_service
    import app.services.user_service as user_service

    monkeypatch.setattr(auth_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(auth_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(user_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(user_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(api_deps, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(core_middleware, "get_redis", lambda: fake_redis)

    monkeypatch.setattr(stats_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(stats_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(stats_service, "get_note_contents", lambda: fake_mongo["note_contents"])
    monkeypatch.setattr(
        stats_service, "get_article_contents", lambda: fake_mongo["article_contents"]
    )
    return fake_db, fake_mongo, fake_redis


@pytest_asyncio.fixture
async def auth(stats_env, client):
    """注册并登录一个用户，返回 (headers, user_id)。"""
    await client.post(
        "/api/v1/auth/register",
        json={"username": "statter", "email": "statter@example.com", "password": "secret123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "statter", "password": "secret123"},
    )
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = await client.get("/api/v1/auth/me", headers=headers)
    return headers, me.json()["data"]["id"]


def _seed(fake_db, fake_mongo, fake_redis, user_id):
    now = datetime.now()
    # 笔记：2 条正常 + 1 条已删除（不计入）
    n1 = Note(user_id=user_id, title="n1", content_id="c1", status=1, is_pinned=0)
    n1.id = 1
    n1.created_at = now
    n2 = Note(user_id=user_id, title="n2", content_id="c2", status=1, is_pinned=0)
    n2.id = 2
    n2.created_at = now - timedelta(days=1)
    n3 = Note(user_id=user_id, title="deleted", content_id="c3", status=0, is_pinned=0)
    n3.id = 3
    n3.created_at = now
    fake_db.rows(Note).extend([n1, n2, n3])

    # 文章：草稿 / 已发布 / 已下架
    a1 = Article(user_id=user_id, title="draft", content_id="a1", status=0, view_count=5)
    a1.id = 1
    a1.created_at = now
    a2 = Article(user_id=user_id, title="published", content_id="a2", status=1, view_count=20)
    a2.id = 2
    a2.created_at = now - timedelta(days=2)
    a3 = Article(user_id=user_id, title="unpublished", content_id="a3", status=2, view_count=3)
    a3.id = 3
    a3.created_at = now
    fake_db.rows(Article).extend([a1, a2, a3])

    # MongoDB 正文字数
    fake_mongo["note_contents"]._docs.extend(
        [{"user_id": user_id, "word_count": 100}, {"user_id": user_id, "word_count": 50}]
    )
    fake_mongo["article_contents"]._docs.append({"user_id": user_id, "word_count": 200})

    # Redis 阅读量增量（未回写 MySQL 的部分）
    fake_redis._hashes["stat:article:view:2"] = {"views": "7"}


@pytest.mark.asyncio
async def test_overview(auth, client, stats_env):
    headers, user_id = auth
    fake_db, fake_mongo, fake_redis = stats_env
    _seed(fake_db, fake_mongo, fake_redis, user_id)

    resp = await client.get("/api/v1/stats/overview", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["note_count"] == 2
    assert data["article_count"] == 3
    assert data["published_count"] == 1
    assert data["draft_count"] == 1
    assert data["total_words"] == 350
    # MySQL 阅读量 5+20+3=28，加上 Redis 未回写增量 7 → 35
    assert data["total_views"] == 35


@pytest.mark.asyncio
async def test_trend_fills_missing_days(auth, client, stats_env):
    headers, user_id = auth
    fake_db, fake_mongo, fake_redis = stats_env
    _seed(fake_db, fake_mongo, fake_redis, user_id)

    resp = await client.get("/api/v1/stats/trend?days=3", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 3

    today = datetime.now().date().isoformat()
    by_date = {d["date"]: d for d in data}
    assert by_date[today]["note_count"] == 1      # 仅 n1（n3 已删除不计）
    assert by_date[today]["article_count"] == 2   # a1 + a3
    assert by_date[(datetime.now().date() - timedelta(days=1)).isoformat()]["note_count"] == 1
    assert by_date[(datetime.now().date() - timedelta(days=2)).isoformat()]["article_count"] == 1


@pytest.mark.asyncio
async def test_stats_require_auth(client):
    resp = await client.get("/api/v1/stats/overview")
    assert resp.status_code == 401
    resp2 = await client.get("/api/v1/stats/trend?days=7")
    assert resp2.status_code == 401
