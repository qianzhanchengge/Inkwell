"""认证拆分测试：工作台 / 博客双会话隔离（基于内存假件）。

覆盖：
- 工作台用户可同时登录两套会话，token scope 正确
- 博客用户不能登录工作台（403）
- 工作台 token 不能用于博客互动接口
- 博客 token 不能用于工作台管理接口
- 两套会话互不影响（登出一方，另一方仍有效）
- 旧 token（无 scope 载荷）仍可用于工作台（向后兼容）
"""
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from jose import jwt

from app.config import settings
from app.core.security import new_jti


@pytest.fixture
def split_env(monkeypatch, fake_redis, fake_db, fake_mongo):
    import app.api.deps as api_deps
    import app.core.middleware as core_middleware
    import app.services.article_service as article_service
    import app.services.auth_service as auth_service
    import app.services.category_service as category_service
    import app.services.note_service as note_service
    import app.services.tag_service as tag_service
    import app.services.user_service as user_service

    async def _noop(*a, **k):
        return None

    monkeypatch.setattr(auth_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(auth_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(user_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(user_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(api_deps, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(core_middleware, "get_redis", lambda: fake_redis)

    monkeypatch.setattr(note_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(note_service, "get_note_contents", lambda: fake_mongo["note_contents"])
    monkeypatch.setattr(note_service, "cache_invalidate_pattern", _noop)
    monkeypatch.setattr(note_service, "cache_get", _noop)
    monkeypatch.setattr(note_service, "cache_set", _noop)

    monkeypatch.setattr(article_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(article_service, "get_article_contents", lambda: fake_mongo["article_contents"])
    monkeypatch.setattr(article_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(article_service, "cache_invalidate_pattern", _noop)
    monkeypatch.setattr(category_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(tag_service, "get_session_factory", lambda: fake_db)
    return fake_db, fake_mongo, fake_redis


async def _register(client, username, path="/api/v1/auth/register"):
    return await client.post(
        path,
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "secret123",
        },
    )


async def _login(client, username, path="/api/v1/auth/login"):
    return await client.post(path, json={"username": username, "password": "secret123"})


def _headers(resp):
    return {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}


@pytest.mark.asyncio
async def test_workbench_user_login_both_scopes(split_env, client):
    """工作台用户既可登录工作台，也可登录博客，两者 scope 不同。"""
    await _register(client, "wb1")

    w_login = await _login(client, "wb1", "/api/v1/auth/login")
    assert w_login.status_code == 200
    assert w_login.json()["data"]["access_token"]

    b_login = await _login(client, "wb1", "/api/v1/blog/auth/login")
    assert b_login.status_code == 200

    from app.core.security import decode_token

    assert decode_token(w_login.json()["data"]["access_token"])["scope"] == "workbench"
    assert decode_token(b_login.json()["data"]["access_token"])["scope"] == "blog"
    # 两套会话互不相同（jti 不同）
    assert (
        decode_token(w_login.json()["data"]["access_token"])["jti"]
        != decode_token(b_login.json()["data"]["access_token"])["jti"]
    )


@pytest.mark.asyncio
async def test_blog_user_cannot_login_workbench(split_env, client):
    """博客注册用户：可登录博客，登录工作台被拒（403）。"""
    reg = await _register(client, "blogger1", "/api/v1/blog/auth/register")
    assert reg.status_code == 200
    assert reg.json()["data"]["user_type"] == 2

    b_login = await _login(client, "blogger1", "/api/v1/blog/auth/login")
    assert b_login.status_code == 200

    w_login = await _login(client, "blogger1", "/api/v1/auth/login")
    assert w_login.status_code == 403
    assert "博客" in w_login.json()["message"]


@pytest.mark.asyncio
async def test_workbench_token_rejected_on_blog_actions(split_env, client):
    """工作台 token 不能点赞/评论（博客互动必须 blog scope）。"""
    await _register(client, "wb2")
    wheaders = _headers(await _login(client, "wb2", "/api/v1/auth/login"))

    created = await client.post(
        "/api/v1/articles", headers=wheaders, json={"title": "T", "content": "C"}
    )
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=wheaders)

    r_like = await client.post(f"/api/v1/articles/{article_id}/like", headers=wheaders)
    assert r_like.status_code == 401

    r_comment = await client.post(
        f"/api/v1/articles/{article_id}/comments", headers=wheaders, json={"content": "x"}
    )
    assert r_comment.status_code == 401


@pytest.mark.asyncio
async def test_blog_token_rejected_on_workbench_actions(split_env, client):
    """博客 token 不能操作工作台管理接口（笔记/文章创建）。"""
    await _register(client, "wb3")
    bheaders = _headers(await _login(client, "wb3", "/api/v1/blog/auth/login"))

    r_note = await client.post(
        "/api/v1/notes", headers=bheaders, json={"title": "n", "content": "c"}
    )
    assert r_note.status_code == 401

    r_article = await client.post(
        "/api/v1/articles", headers=bheaders, json={"title": "a", "content": "c"}
    )
    assert r_article.status_code == 401


@pytest.mark.asyncio
async def test_workbench_logout_keeps_blog_session(split_env, client):
    """工作台登出不影响博客会话。"""
    await _register(client, "wb4")
    wheaders = _headers(await _login(client, "wb4", "/api/v1/auth/login"))
    bheaders = _headers(await _login(client, "wb4", "/api/v1/blog/auth/login"))

    assert (await client.post("/api/v1/auth/logout", headers=wheaders)).status_code == 200
    assert (await client.get("/api/v1/auth/me", headers=wheaders)).status_code == 401

    me = await client.get("/api/v1/blog/auth/me", headers=bheaders)
    assert me.status_code == 200
    assert me.json()["data"]["username"] == "wb4"


@pytest.mark.asyncio
async def test_blog_logout_keeps_workbench_session(split_env, client):
    """博客登出不影响工作台会话。"""
    await _register(client, "wb5")
    wheaders = _headers(await _login(client, "wb5", "/api/v1/auth/login"))
    bheaders = _headers(await _login(client, "wb5", "/api/v1/blog/auth/login"))

    assert (await client.post("/api/v1/blog/auth/logout", headers=bheaders)).status_code == 200
    assert (await client.get("/api/v1/blog/auth/me", headers=bheaders)).status_code == 401

    me = await client.get("/api/v1/auth/me", headers=wheaders)
    assert me.status_code == 200


@pytest.mark.asyncio
async def test_legacy_token_without_scope_still_works(split_env, client):
    """旧 token（载荷无 scope）视为 workbench，仍可访问工作台接口。"""
    await _register(client, "wb6")
    wheaders = _headers(await _login(client, "wb6", "/api/v1/auth/login"))
    me = await client.get("/api/v1/auth/me", headers=wheaders)
    user_id = me.json()["data"]["id"]

    legacy_payload = {
        "sub": str(user_id),
        "username": "wb6",
        "jti": new_jti(),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    legacy = jwt.encode(
        legacy_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {legacy}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["username"] == "wb6"


@pytest.mark.asyncio
async def test_blog_refresh_rejects_workbench_token(split_env, client):
    """博客刷新接口拒绝工作台 refresh token（作用域不匹配）。"""
    await _register(client, "wb7")
    w_login = await _login(client, "wb7", "/api/v1/auth/login")
    w_refresh = w_login.json()["data"]["refresh_token"]

    resp = await client.post("/api/v1/blog/auth/refresh", json={"refresh_token": w_refresh})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_blog_refresh_works_for_blog_token(split_env, client):
    """博客 refresh 可正常换发博客 token。"""
    await _register(client, "wb8")
    b_login = await _login(client, "wb8", "/api/v1/blog/auth/login")
    b_refresh = b_login.json()["data"]["refresh_token"]

    resp = await client.post("/api/v1/blog/auth/refresh", json={"refresh_token": b_refresh})
    assert resp.status_code == 200

    from app.core.security import decode_token

    assert decode_token(resp.json()["data"]["access_token"])["scope"] == "blog"
