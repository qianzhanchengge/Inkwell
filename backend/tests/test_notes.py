"""笔记 / 分类 / 标签接口测试（Phase 3，基于内存假件，不依赖真实数据库）。"""
import pytest
import pytest_asyncio


@pytest.fixture
def notes_env(monkeypatch, fake_redis, fake_db, fake_mongo):
    """把认证、用户、笔记、分类、标签服务用到的 Redis/DB/Mongo 替换为内存假件。"""
    import app.api.deps as api_deps
    import app.core.middleware as core_middleware
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
    # 列表读缓存在单测中用 noop（缓存命中返回 None = 未命中；写缓存不落盘）
    monkeypatch.setattr(note_service, "cache_get", _noop)
    monkeypatch.setattr(note_service, "cache_set", _noop)
    monkeypatch.setattr(category_service, "get_session_factory", lambda: fake_db)
    monkeypatch.setattr(tag_service, "get_session_factory", lambda: fake_db)
    return fake_db, fake_mongo


@pytest_asyncio.fixture
async def auth(notes_env, client):
    """注册并登录一个用户，返回 (headers, user_id)。"""
    await client.post(
        "/api/v1/auth/register",
        json={"username": "noter", "email": "noter@example.com", "password": "secret123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "noter", "password": "secret123"},
    )
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = await client.get("/api/v1/auth/me", headers=headers)
    user_id = me.json()["data"]["id"]
    return headers, user_id


async def _create_note(client, headers, body=None):
    resp = await client.post("/api/v1/notes", headers=headers, json=body or {
        "title": "学习笔记",
        "content": "# 标题\n\n这是正文 FastAPI",
        "tags": ["Python", "FastAPI"],
    })
    return resp


# --------------------------------------------------------------------------- #
# 笔记
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_create_note_with_tags(auth, client):
    headers, _ = auth
    resp = await _create_note(client, headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["title"] == "学习笔记"
    assert data["content"].startswith("# 标题")
    assert data["content_html"]
    assert data["word_count"] > 0
    tag_names = {t["name"] for t in data["tags"]}
    assert tag_names == {"Python", "FastAPI"}
    assert data["is_pinned"] is False


@pytest.mark.asyncio
async def test_list_notes_pagination(auth, client):
    headers, _ = auth
    for i in range(3):
        await _create_note(client, headers, {"title": f"笔记{i}", "content": "正文"})
    resp = await client.get("/api/v1/notes?page=1&page_size=2", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 3
    assert data["total_pages"] == 2
    assert len(data["items"]) == 2

    resp2 = await client.get("/api/v1/notes?page=2&page_size=2", headers=headers)
    assert len(resp2.json()["data"]["items"]) == 1


@pytest.mark.asyncio
async def test_list_notes_filter_by_keyword(auth, client):
    headers, _ = auth
    await _create_note(client, headers, {"title": "关于Python", "content": "正文"})
    await _create_note(client, headers, {"title": "关于前端", "content": "正文"})
    resp = await client.get("/api/v1/notes?keyword=Python", headers=headers)
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "关于Python"


@pytest.mark.asyncio
async def test_get_note_detail(auth, client):
    headers, _ = auth
    created = await _create_note(client, headers)
    note_id = created.json()["data"]["id"]
    resp = await client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == note_id
    assert data["content"].startswith("# 标题")
    assert {t["name"] for t in data["tags"]} == {"Python", "FastAPI"}


@pytest.mark.asyncio
async def test_update_note_content_increments_version(auth, client, notes_env):
    headers, _ = auth
    _, fake_mongo = notes_env
    created = await _create_note(client, headers)
    note_id = created.json()["data"]["id"]

    resp = await client.put(
        f"/api/v1/notes/{note_id}",
        headers=headers,
        json={"content": "# 新标题\n\n新正文"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["content"] == "# 新标题\n\n新正文"

    doc = fake_mongo["note_contents"]._docs[0]
    assert doc["note_id"] == note_id
    assert doc["version"] == 2


@pytest.mark.asyncio
async def test_update_note_tags(auth, client):
    headers, _ = auth
    created = await _create_note(client, headers)
    note_id = created.json()["data"]["id"]
    resp = await client.put(
        f"/api/v1/notes/{note_id}",
        headers=headers,
        json={"tags": ["新标签"]},
    )
    assert resp.status_code == 200
    assert {t["name"] for t in resp.json()["data"]["tags"]} == {"新标签"}


@pytest.mark.asyncio
async def test_delete_note_soft(auth, client):
    headers, _ = auth
    created = await _create_note(client, headers)
    note_id = created.json()["data"]["id"]
    resp = await client.delete(f"/api/v1/notes/{note_id}", headers=headers)
    assert resp.status_code == 200
    get = await client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert get.status_code == 404


@pytest.mark.asyncio
async def test_toggle_pin(auth, client):
    headers, _ = auth
    created = await _create_note(client, headers)
    note_id = created.json()["data"]["id"]
    resp = await client.patch(f"/api/v1/notes/{note_id}/pin", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["is_pinned"] is True


@pytest.mark.asyncio
async def test_search_notes(auth, client):
    headers, _ = auth
    await _create_note(client, headers, {"title": "A", "content": "包含 FastAPI 关键字的内容"})
    await _create_note(client, headers, {"title": "B", "content": "无关内容"})
    resp = await client.get("/api/v1/notes/search?keyword=FastAPI", headers=headers)
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "A"


@pytest.mark.asyncio
async def test_note_not_found_for_other_user(auth, client):
    headers, user_id = auth
    created = await _create_note(client, headers)
    note_id = created.json()["data"]["id"]

    # 注册另一个用户，尝试访问不属于自己的笔记 → 404
    await client.post(
        "/api/v1/auth/register",
        json={"username": "other", "email": "other@example.com", "password": "secret123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "other", "password": "secret123"},
    )
    other_headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    resp = await client.get(f"/api/v1/notes/{note_id}", headers=other_headers)
    assert resp.status_code == 404


# --------------------------------------------------------------------------- #
# 分类
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_category_crud(auth, client):
    headers, _ = auth
    created = await client.post(
        "/api/v1/categories", headers=headers, json={"name": "技术", "type": 1}
    )
    assert created.status_code == 200
    cat_id = created.json()["data"]["id"]

    listed = await client.get("/api/v1/categories?type=1", headers=headers)
    assert [c["name"] for c in listed.json()["data"]] == ["技术"]

    updated = await client.put(
        f"/api/v1/categories/{cat_id}", headers=headers, json={"name": "技术学习"}
    )
    assert updated.json()["data"]["name"] == "技术学习"

    deleted = await client.delete(f"/api/v1/categories/{cat_id}", headers=headers)
    assert deleted.status_code == 200


@pytest.mark.asyncio
async def test_delete_category_nulls_note(auth, client):
    headers, _ = auth
    cat = await client.post(
        "/api/v1/categories", headers=headers, json={"name": "技术", "type": 1}
    )
    cat_id = cat.json()["data"]["id"]
    created = await _create_note(client, headers, {
        "title": "有分类的笔记", "content": "正文", "category_id": cat_id,
    })
    note_id = created.json()["data"]["id"]
    assert created.json()["data"]["category"]["id"] == cat_id

    await client.delete(f"/api/v1/categories/{cat_id}", headers=headers)
    get = await client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert get.json()["data"]["category"] is None


# --------------------------------------------------------------------------- #
# 标签
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_tag_crud(auth, client):
    headers, _ = auth
    created = await client.post("/api/v1/tags", headers=headers, json={"name": "Python"})
    assert created.status_code == 200
    tag_id = created.json()["data"]["id"]

    listed = await client.get("/api/v1/tags", headers=headers)
    assert [t["name"] for t in listed.json()["data"]] == ["Python"]

    deleted = await client.delete(f"/api/v1/tags/{tag_id}", headers=headers)
    assert deleted.status_code == 200
    listed2 = await client.get("/api/v1/tags", headers=headers)
    assert listed2.json()["data"] == []


@pytest.mark.asyncio
async def test_delete_tag_cleans_note_association(auth, client):
    headers, _ = auth
    created = await _create_note(client, headers, {"title": "带标签", "content": "正文", "tags": ["Python"]})
    note_id = created.json()["data"]["id"]
    tag_id = created.json()["data"]["tags"][0]["id"]

    await client.delete(f"/api/v1/tags/{tag_id}", headers=headers)

    get = await client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert get.json()["data"]["tags"] == []


@pytest.mark.asyncio
async def test_list_notes_by_tag(auth, client):
    """§5.4：列表支持按标签筛选。"""
    headers, _ = auth
    n1 = await _create_note(client, headers, {"title": "带标签甲", "content": "正文", "tags": ["甲"]})
    tag_id = n1.json()["data"]["tags"][0]["id"]
    await _create_note(client, headers, {"title": "带标签乙", "content": "正文", "tags": ["乙"]})
    resp = await client.get(f"/api/v1/notes?tag_id={tag_id}", headers=headers)
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "带标签甲"


@pytest.mark.asyncio
async def test_search_total_after_soft_delete(auth, client):
    """搜索 total 以 MySQL 有效笔记数为准（软删除后不计入命中数）。"""
    headers, _ = auth
    created = await _create_note(client, headers, {"title": "将被删", "content": "独特关键字Z9KQ正文"})
    note_id = created.json()["data"]["id"]
    resp = await client.get("/api/v1/notes/search?keyword=Z9KQ", headers=headers)
    assert resp.json()["data"]["total"] == 1
    await client.delete(f"/api/v1/notes/{note_id}", headers=headers)
    resp = await client.get("/api/v1/notes/search?keyword=Z9KQ", headers=headers)
    data = resp.json()["data"]
    assert data["total"] == 0
    assert data["items"] == []
