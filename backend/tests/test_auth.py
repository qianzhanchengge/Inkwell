"""认证接口测试骨架。"""
import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["code"] == 200


@pytest.mark.asyncio
async def test_register_validation(client):
    # 缺少必填字段时返回 422（Pydantic 校验）
    resp = await client.post("/api/v1/auth/register", json={"username": "a"})
    assert resp.status_code == 422
