"""文章接口测试（Phase 4，基于内存假件，不依赖真实数据库）。"""
import pytest
import pytest_asyncio


@pytest.fixture
def articles_env(monkeypatch, fake_redis, fake_db, fake_mongo):
    """把认证、用户、文章、分类、标签服务用到的 Redis/DB/Mongo 替换为内存假件。"""
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
async def auth(articles_env, client):
    """注册并登录一个用户，返回 (headers, user_id)。"""
    await client.post(
        "/api/v1/auth/register",
        json={"username": "author", "email": "author@example.com", "password": "secret123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "author", "password": "secret123"},
    )
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = await client.get("/api/v1/auth/me", headers=headers)
    return headers, me.json()["data"]["id"]


@pytest_asyncio.fixture
async def blog_auth(auth, client):
    """博客会话头（同一用户在博客侧单独登录；点赞/收藏/分享需 blog scope）。"""
    resp = await client.post(
        "/api/v1/blog/auth/login",
        json={"username": "author", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}


async def _create(client, headers, body=None):
    return await client.post("/api/v1/articles", headers=headers, json=body or {
        "title": "深入理解 Python 异步编程",
        "summary": "本文介绍 Python 异步编程的原理与实践",
        "content": "# 异步编程\n\n这是正文 FastAPI 内容",
        "tags": ["Python", "异步"],
    })


# --------------------------------------------------------------------------- #
# 创建与发布流程
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_create_article_draft(auth, client):
    headers, _ = auth
    resp = await _create(client, headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == 0
    assert data["title"] == "深入理解 Python 异步编程"
    assert data["content"].startswith("# 异步编程")
    assert data["content_html"]
    assert {t["name"] for t in data["tags"]} == {"Python", "异步"}


@pytest.mark.asyncio
async def test_publish_article_flow(auth, client):
    headers, _ = auth
    created = await _create(client, headers)
    article_id = created.json()["data"]["id"]

    resp = await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == 1
    assert resp.json()["data"]["published_at"] is not None


@pytest.mark.asyncio
async def test_publish_only_draft(auth, client):
    headers, _ = auth
    created = await _create(client, headers)
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)

    resp = await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_unpublish_article(auth, client):
    headers, _ = auth
    created = await _create(client, headers)
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)

    resp = await client.post(f"/api/v1/articles/{article_id}/unpublish", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == 2


# --------------------------------------------------------------------------- #
# 列表
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_public_list_only_published(auth, client):
    headers, _ = auth
    await _create(client, headers, {"title": "草稿", "content": "正文"})
    pub = await _create(client, headers, {"title": "已发布", "content": "正文"})
    await client.post(f"/api/v1/articles/{pub.json()['data']['id']}/publish", headers=headers)

    resp = await client.get("/api/v1/articles")
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "已发布"


@pytest.mark.asyncio
async def test_mine_list_filter_by_status(auth, client):
    headers, _ = auth
    await _create(client, headers, {"title": "草稿A", "content": "正文"})
    pub = await _create(client, headers, {"title": "已发布B", "content": "正文"})
    await client.post(f"/api/v1/articles/{pub.json()['data']['id']}/publish", headers=headers)

    resp = await client.get("/api/v1/articles/mine?status=1", headers=headers)
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "已发布B"

    resp2 = await client.get("/api/v1/articles/mine?status=0", headers=headers)
    assert resp2.json()["data"]["total"] == 1
    assert resp2.json()["data"]["items"][0]["title"] == "草稿A"


# --------------------------------------------------------------------------- #
# 详情与阅读量
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_get_article_detail(auth, client):
    headers, _ = auth
    cat = await client.post("/api/v1/categories", headers=headers, json={"name": "技术", "type": 2})
    cat_id = cat.json()["data"]["id"]
    created = await _create(client, headers, {"title": "分类文章", "content": "正文", "category_id": cat_id})
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)

    resp = await client.get(f"/api/v1/articles/{article_id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["title"] == "分类文章"
    assert data["content"] == "正文"
    assert data["category"]["name"] == "技术"


@pytest.mark.asyncio
async def test_view_count_increments_on_public_detail(auth, client):
    headers, _ = auth
    created = await _create(client, headers)
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)

    first = await client.get(f"/api/v1/articles/{article_id}")
    second = await client.get(f"/api/v1/articles/{article_id}")
    assert first.json()["data"]["view_count"] == 1
    assert second.json()["data"]["view_count"] == 2


@pytest.mark.asyncio
async def test_public_detail_without_auth(auth, client):
    headers, _ = auth
    created = await _create(client, headers)
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)

    resp = await client.get(f"/api/v1/articles/{article_id}")  # 无 token
    assert resp.status_code == 200


# --------------------------------------------------------------------------- #
# 点赞
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_like_and_unlike(auth, blog_auth, client):
    headers, _ = auth
    created = await _create(client, headers)
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)

    liked = await client.post(f"/api/v1/articles/{article_id}/like", headers=blog_auth)
    assert liked.json()["data"]["liked"] is True
    assert liked.json()["data"]["like_count"] == 1

    unliked = await client.post(f"/api/v1/articles/{article_id}/like", headers=blog_auth)
    assert unliked.json()["data"]["liked"] is False
    assert unliked.json()["data"]["like_count"] == 0


@pytest.mark.asyncio
async def test_like_draft_rejected(auth, blog_auth, client):
    headers, _ = auth
    created = await _create(client, headers)  # 草稿
    article_id = created.json()["data"]["id"]

    resp = await client.post(f"/api/v1/articles/{article_id}/like", headers=blog_auth)
    assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# 更新与删除
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_update_article_content_increments_version(auth, client, articles_env):
    headers, _ = auth
    _, fake_mongo, _ = articles_env
    created = await _create(client, headers)
    article_id = created.json()["data"]["id"]

    resp = await client.put(
        f"/api/v1/articles/{article_id}",
        headers=headers,
        json={"content": "# 新标题\n\n新正文"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["content"] == "# 新标题\n\n新正文"

    doc = fake_mongo["article_contents"]._docs[0]
    assert doc["article_id"] == article_id
    assert doc["version"] == 2


@pytest.mark.asyncio
async def test_delete_article_removes_content(auth, client, articles_env):
    headers, _ = auth
    _, fake_mongo, _ = articles_env
    created = await _create(client, headers)
    article_id = created.json()["data"]["id"]

    resp = await client.delete(f"/api/v1/articles/{article_id}", headers=headers)
    assert resp.status_code == 200

    get = await client.get(f"/api/v1/articles/{article_id}", headers=headers)
    assert get.status_code == 404
    assert fake_mongo["article_contents"]._docs == []


# --------------------------------------------------------------------------- #
# 越权与搜索
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_draft_not_visible_to_other_user(auth, client):
    headers, _ = auth
    created = await _create(client, headers)  # 草稿
    article_id = created.json()["data"]["id"]

    await client.post(
        "/api/v1/auth/register",
        json={"username": "other", "email": "other@example.com", "password": "secret123"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"username": "other", "password": "secret123"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    resp = await client.get(f"/api/v1/articles/{article_id}", headers=other_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_search_articles_published_only(auth, client):
    headers, _ = auth
    draft = await _create(client, headers, {"title": "草稿", "content": "包含 UniqueKeyword 的草稿正文"})
    pub = await _create(client, headers, {"title": "已发布", "content": "包含 UniqueKeyword 的已发布正文"})
    await client.post(f"/api/v1/articles/{pub.json()['data']['id']}/publish", headers=headers)

    resp = await client.get("/api/v1/articles/search?keyword=UniqueKeyword")
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "已发布"
