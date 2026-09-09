"""博客前台聚合接口测试（§5.5，基于内存假件）。"""
import pytest
import pytest_asyncio


@pytest.fixture
def blog_env(monkeypatch, fake_redis, fake_db, fake_mongo):
    import app.api.deps as api_deps
    import app.core.middleware as core_middleware
    import app.services.auth_service as auth_service
    import app.services.article_service as article_service
    import app.services.blog_service as blog_service
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
    monkeypatch.setattr(blog_service, "get_session_factory", lambda: fake_db)
    return fake_db, fake_mongo, fake_redis


@pytest_asyncio.fixture
async def auth(blog_env, client):
    await client.post(
        "/api/v1/auth/register",
        json={"username": "blogger", "email": "blogger@example.com", "password": "secret123"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"username": "blogger", "password": "secret123"}
    )
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    me = await client.get("/api/v1/auth/me", headers=headers)
    return headers, me.json()["data"]["id"]


async def _publish(client, headers, body=None):
    created = await client.post(
        "/api/v1/articles",
        headers=headers,
        json=body
        or {"title": "文章", "summary": "摘要", "content": "正文", "tags": ["Python"]},
    )
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)
    return article_id


@pytest.mark.asyncio
async def test_feed_only_published(auth, client):
    headers, _ = auth
    await client.post(
        "/api/v1/articles", headers=headers, json={"title": "草稿", "content": "正文"}
    )  # 草稿
    await _publish(client, headers, {"title": "已发布", "content": "正文"})

    resp = await client.get("/api/v1/blog/feed")
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "已发布"


@pytest.mark.asyncio
async def test_feed_hot_sort(auth, client):
    headers, _ = auth
    await _publish(client, headers, {"title": "A", "content": "正文"})
    await _publish(client, headers, {"title": "B", "content": "正文"})

    resp = await client.get("/api/v1/blog/feed?sort=hot")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 2


@pytest.mark.asyncio
async def test_hot_list(auth, client):
    headers, _ = auth
    await _publish(client, headers, {"title": "热门", "content": "正文"})
    resp = await client.get("/api/v1/blog/hot?top_n=5")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_category_stats(auth, client):
    headers, _ = auth
    cat = await client.post(
        "/api/v1/categories", headers=headers, json={"name": "技术", "type": 2}
    )
    cat_id = cat.json()["data"]["id"]
    await _publish(client, headers, {"title": "分类文章", "content": "正文", "category_id": cat_id})

    resp = await client.get("/api/v1/blog/categories")
    items = resp.json()["data"]
    assert any(c["name"] == "技术" and c["article_count"] == 1 for c in items)


@pytest.mark.asyncio
async def test_tag_cloud(auth, client):
    headers, _ = auth
    await _publish(client, headers, {"title": "带标签", "content": "正文", "tags": ["FastAPI"]})

    resp = await client.get("/api/v1/blog/tags")
    items = resp.json()["data"]
    assert any(t["name"] == "FastAPI" and t["use_count"] == 1 for t in items)


@pytest.mark.asyncio
async def test_archive(auth, client):
    headers, _ = auth
    await _publish(client, headers, {"title": "归档文", "content": "正文"})

    resp = await client.get("/api/v1/blog/archive")
    assert len(resp.json()["data"]) >= 1
    assert resp.json()["data"][0]["count"] == 1


@pytest.mark.asyncio
async def test_related_excludes_self_and_same_category(auth, client):
    headers, _ = auth
    cat = await client.post(
        "/api/v1/categories", headers=headers, json={"name": "同分类", "type": 2}
    )
    cat_id = cat.json()["data"]["id"]
    a1 = await _publish(client, headers, {"title": "文章一", "content": "正文", "category_id": cat_id})
    a2 = await _publish(client, headers, {"title": "文章二", "content": "正文", "category_id": cat_id})

    resp = await client.get(f"/api/v1/blog/related/{a1}?top_n=5")
    items = resp.json()["data"]
    assert any(i["id"] == a2 for i in items)
    assert all(i["id"] != a1 for i in items)


@pytest.mark.asyncio
async def test_feed_filter_by_category(auth, client):
    headers, _ = auth
    cat = await client.post(
        "/api/v1/categories", headers=headers, json={"name": "技术", "type": 2}
    )
    cat_id = cat.json()["data"]["id"]
    await _publish(client, headers, {"title": "分类文", "content": "正文", "category_id": cat_id})
    await _publish(client, headers, {"title": "无分类", "content": "正文"})
    resp = await client.get(f"/api/v1/blog/feed?category_id={cat_id}")
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "分类文"


@pytest.mark.asyncio
async def test_feed_filter_by_tag(auth, client):
    headers, _ = auth
    await _publish(client, headers, {"title": "Python文", "content": "正文", "tags": ["Python"]})
    await _publish(client, headers, {"title": "Java文", "content": "正文", "tags": ["Java"]})
    resp = await client.get("/api/v1/blog/feed?tag=Python")
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python文"
