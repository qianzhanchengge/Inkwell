"""评论接口测试（博客系统，基于内存假件）。"""
import pytest
import pytest_asyncio


@pytest.fixture
def comments_env(monkeypatch, fake_redis, fake_db, fake_mongo):
    import app.api.deps as api_deps
    import app.core.middleware as core_middleware
    import app.services.auth_service as auth_service
    import app.services.article_service as article_service
    import app.services.category_service as category_service
    import app.services.comment_service as comment_service
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
    monkeypatch.setattr(comment_service, "get_session_factory", lambda: fake_db)
    return fake_db, fake_mongo, fake_redis


async def _register_login(client, username):
    await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "secret123"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": "secret123"}
    )
    return {"Authorization": f"Bearer {login.json()['data']['access_token']}"}


@pytest_asyncio.fixture
async def author(comments_env, client):
    headers = await _register_login(client, "author")
    me = await client.get("/api/v1/auth/me", headers=headers)
    return headers, me.json()["data"]["id"]


async def _published_article(client, headers):
    created = await client.post(
        "/api/v1/articles",
        headers=headers,
        json={"title": "文章", "summary": "摘要", "content": "正文"},
    )
    article_id = created.json()["data"]["id"]
    await client.post(f"/api/v1/articles/{article_id}/publish", headers=headers)
    return article_id


@pytest.mark.asyncio
async def test_create_and_list_comment(author, client):
    headers, _ = author
    article_id = await _published_article(client, headers)

    created = await client.post(
        f"/api/v1/articles/{article_id}/comments",
        headers=headers,
        json={"content": "写得太好了"},
    )
    assert created.status_code == 200
    data = created.json()["data"]
    assert data["content"] == "写得太好了"
    assert data["parent_id"] is None
    assert data["author_nickname"] == "author"

    resp = await client.get(f"/api/v1/articles/{article_id}/comments")
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_create_reply(author, client):
    headers, _ = author
    article_id = await _published_article(client, headers)
    parent = await client.post(
        f"/api/v1/articles/{article_id}/comments", headers=headers, json={"content": "一楼"}
    )
    parent_id = parent.json()["data"]["id"]

    reply = await client.post(
        f"/api/v1/articles/{article_id}/comments",
        headers=headers,
        json={"content": "回复一楼", "parent_id": parent_id, "reply_to_user_id": parent.json()["data"]["user_id"]},
    )
    data = reply.json()["data"]
    assert data["parent_id"] == parent_id
    assert data["reply_to_user_id"] == parent.json()["data"]["user_id"]


@pytest.mark.asyncio
async def test_comment_requires_login(author, client):
    headers, _ = author
    article_id = await _published_article(client, headers)
    resp = await client.post(f"/api/v1/articles/{article_id}/comments", json={"content": "匿名"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_comment_on_draft_rejected(author, client):
    headers, _ = author
    created = await client.post(
        "/api/v1/articles", headers=headers, json={"title": "草稿", "content": "正文"}
    )
    article_id = created.json()["data"]["id"]  # 未发布

    resp = await client.post(
        f"/api/v1/articles/{article_id}/comments", headers=headers, json={"content": "评论"}
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_own_comment(author, client):
    headers, _ = author
    article_id = await _published_article(client, headers)
    created = await client.post(
        f"/api/v1/articles/{article_id}/comments", headers=headers, json={"content": "要删"}
    )
    comment_id = created.json()["data"]["id"]

    resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=headers)
    assert resp.status_code == 200

    lst = await client.get(f"/api/v1/articles/{article_id}/comments")
    assert lst.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_delete_other_comment_forbidden(author, client, comments_env):
    headers, _ = author
    article_id = await _published_article(client, headers)
    created = await client.post(
        f"/api/v1/articles/{article_id}/comments", headers=headers, json={"content": "作者评论"}
    )
    comment_id = created.json()["data"]["id"]

    other = await _register_login(client, "commenter")
    resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=other)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_author_can_delete_commenter_comment(author, client, comments_env):
    headers, _ = author
    article_id = await _published_article(client, headers)
    commenter = await _register_login(client, "commenter")
    created = await client.post(
        f"/api/v1/articles/{article_id}/comments",
        headers=commenter,
        json={"content": "访客评论"},
    )
    comment_id = created.json()["data"]["id"]

    resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_toggle_comment_like(author, client):
    headers, _ = author
    article_id = await _published_article(client, headers)
    created = await client.post(
        f"/api/v1/articles/{article_id}/comments", headers=headers, json={"content": "点赞我"}
    )
    comment_id = created.json()["data"]["id"]

    r1 = await client.post(f"/api/v1/comments/{comment_id}/like", headers=headers)
    assert r1.json()["data"]["liked"] is True
    assert r1.json()["data"]["like_count"] == 1

    r2 = await client.post(f"/api/v1/comments/{comment_id}/like", headers=headers)
    assert r2.json()["data"]["liked"] is False
    assert r2.json()["data"]["like_count"] == 0
