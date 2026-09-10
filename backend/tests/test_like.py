"""点赞/收藏/分享接口测试（博客系统，基于内存假件）。

认证拆分后：文章管理用工作台会话（workbench），点赞/收藏/分享用博客会话（blog）。
"""
import pytest
import pytest_asyncio


@pytest.fixture
def like_env(monkeypatch, fake_redis, fake_db, fake_mongo):
    import app.api.deps as api_deps
    import app.core.middleware as core_middleware
    import app.services.auth_service as auth_service
    import app.services.article_service as article_service
    import app.services.category_service as category_service
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

    monkeypatch.setattr(article_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(article_service, "get_article_contents", lambda: fake_mongo["article_contents"])
    monkeypatch.setattr(article_service, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(article_service, "cache_invalidate_pattern", _noop)
    monkeypatch.setattr(category_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(tag_service, "get_session_factory", lambda: fake_db)
    return fake_db, fake_mongo, fake_redis


@pytest_asyncio.fixture
async def auth(like_env, client):
    """返回 (工作台头, 博客头, 用户 ID)。"""
    await client.post(
        "/api/v1/auth/register",
        json={"username": "liker", "email": "liker@example.com", "password": "secret123"},
    )
    w_login = await client.post(
        "/api/v1/auth/login", json={"username": "liker", "password": "secret123"}
    )
    workbench = {"Authorization": f"Bearer {w_login.json()['data']['access_token']}"}
    b_login = await client.post(
        "/api/v1/blog/auth/login", json={"username": "liker", "password": "secret123"}
    )
    blog = {"Authorization": f"Bearer {b_login.json()['data']['access_token']}"}
    me = await client.get("/api/v1/auth/me", headers=workbench)
    return workbench, blog, me.json()["data"]["id"]


async def _publish(client, headers, title="文章"):
    created = await client.post(
        "/api/v1/articles",
        headers=headers,
        json={"title": title, "summary": "摘要", "content": "正文内容"},
    )
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)
    return article_id


@pytest.mark.asyncio
async def test_like_toggle_dedup(auth, client):
    """点赞去重：同一用户重复点赞会取消（toggle）。"""
    wheaders, bheaders, _ = auth
    article_id = await _publish(client, wheaders)

    r1 = await client.post(f"/api/v1/articles/{article_id}/like", headers=bheaders)
    assert r1.json()["data"]["liked"] is True
    assert r1.json()["data"]["like_count"] == 1

    r2 = await client.post(f"/api/v1/articles/{article_id}/like", headers=bheaders)
    assert r2.json()["data"]["liked"] is False
    assert r2.json()["data"]["like_count"] == 0

    r3 = await client.post(f"/api/v1/articles/{article_id}/like", headers=bheaders)
    assert r3.json()["data"]["liked"] is True
    assert r3.json()["data"]["like_count"] == 1


@pytest.mark.asyncio
async def test_like_requires_login(auth, client):
    wheaders, _, _ = auth
    article_id = await _publish(client, wheaders)
    resp = await client.post(f"/api/v1/articles/{article_id}/like")  # 无 token
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_like_rejects_workbench_token(auth, client):
    """工作台会话不能用于博客点赞（必须博客单独登录）。"""
    wheaders, _, _ = auth
    article_id = await _publish(client, wheaders)
    resp = await client.post(f"/api/v1/articles/{article_id}/like", headers=wheaders)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_like_status_endpoint(auth, client):
    wheaders, bheaders, _ = auth
    article_id = await _publish(client, wheaders)

    # 未点赞（带博客 token）
    r = await client.get(f"/api/v1/articles/{article_id}/like", headers=bheaders)
    assert r.json()["data"]["liked"] is False
    # 未登录
    r = await client.get(f"/api/v1/articles/{article_id}/like")
    assert r.json()["data"]["liked"] is False

    await client.post(f"/api/v1/articles/{article_id}/like", headers=bheaders)
    r = await client.get(f"/api/v1/articles/{article_id}/like", headers=bheaders)
    assert r.json()["data"]["liked"] is True


@pytest.mark.asyncio
async def test_favorite_toggle(auth, client):
    wheaders, bheaders, _ = auth
    article_id = await _publish(client, wheaders)

    r1 = await client.post(f"/api/v1/articles/{article_id}/favorite", headers=bheaders)
    assert r1.json()["data"]["favorited"] is True
    r2 = await client.post(f"/api/v1/articles/{article_id}/favorite", headers=bheaders)
    assert r2.json()["data"]["favorited"] is False


@pytest.mark.asyncio
async def test_list_favorites(auth, client):
    wheaders, bheaders, _ = auth
    a1 = await _publish(client, wheaders, "收藏A")
    a2 = await _publish(client, wheaders, "收藏B")
    await client.post(f"/api/v1/articles/{a1}/favorite", headers=bheaders)
    await client.post(f"/api/v1/articles/{a2}/favorite", headers=bheaders)

    resp = await client.get("/api/v1/articles/favorites", headers=bheaders)
    data = resp.json()["data"]
    assert data["total"] == 2
    assert {i["id"] for i in data["items"]} == {a1, a2}


@pytest.mark.asyncio
async def test_share_records_and_counts(auth, client):
    wheaders, bheaders, _ = auth
    article_id = await _publish(client, wheaders)

    r = await client.post(f"/api/v1/articles/{article_id}/share", headers=bheaders)
    assert r.json()["data"]["shared"] is True
    assert r.json()["data"]["url"] == f"/blog/articles/{article_id}"

    detail = await client.get(f"/api/v1/articles/{article_id}", headers=wheaders)
    assert detail.json()["data"]["share_count"] == 1


@pytest.mark.asyncio
async def test_share_allows_guest(auth, client):
    """分享对游客开放（不记录用户）。"""
    wheaders, _, _ = auth
    article_id = await _publish(client, wheaders)
    r = await client.post(f"/api/v1/articles/{article_id}/share")
    assert r.status_code == 200
    assert r.json()["data"]["shared"] is True
