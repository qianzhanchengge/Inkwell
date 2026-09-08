"""认证 / 用户系统测试（Phase 2，基于内存假件，不依赖真实数据库）。"""
import pytest

REGISTER_BODY = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "secret123",
    "nickname": "Alice",
}


@pytest.fixture
def registered(auth_env, client):
    """注册一个用户并返回其响应。"""

    async def _do(body=None):
        return await client.post("/api/v1/auth/register", json=body or REGISTER_BODY)

    return _do


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["code"] == 200


@pytest.mark.asyncio
async def test_register_validation(client):
    resp = await client.post("/api/v1/auth/register", json={"username": "a"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_success(registered):
    resp = await registered()
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username(registered):
    await registered()
    resp = await registered()
    assert resp.status_code == 409
    assert resp.json()["code"] == 409


@pytest.mark.asyncio
async def test_register_duplicate_email(registered):
    await registered()
    body = {**REGISTER_BODY, "username": "bob", "email": "alice@example.com"}
    resp = await registered(body)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(registered, client):
    await registered()
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "secret123"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(registered, client):
    await registered()
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "wrong-pass"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(registered, client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "ghost", "password": "whatever"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_token(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_invalidates_token(registered, client):
    await registered()
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "secret123"},
    )
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_before = await client.get("/api/v1/auth/me", headers=headers)
    assert me_before.status_code == 200

    logout = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout.status_code == 200

    me_after = await client.get("/api/v1/auth/me", headers=headers)
    assert me_after.status_code == 401


@pytest.mark.asyncio
async def test_change_password_invalidates_old_token(registered, client):
    await registered()
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "secret123"},
    )
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.put(
        "/api/v1/users/password",
        headers=headers,
        json={"old_password": "secret123", "new_password": "newsecret456"},
    )
    assert resp.status_code == 200

    me_after = await client.get("/api/v1/auth/me", headers=headers)
    assert me_after.status_code == 401


@pytest.mark.asyncio
async def test_refresh_flow(registered, client):
    await registered()
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "secret123"},
    )
    refresh_token = login.json()["data"]["refresh_token"]

    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.asyncio
async def test_login_rate_limit(registered, client):
    """登录接口限流：1 分钟窗口内第 6 次请求返回 429。"""
    for _ in range(5):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "alice", "password": "wrong"},
        )
        assert resp.status_code in (200, 401, 404)

    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "wrong"},
    )
    assert resp.status_code == 429
    assert resp.json()["code"] == 429
