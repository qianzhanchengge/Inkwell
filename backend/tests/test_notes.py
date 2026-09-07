"""笔记接口测试骨架。"""
import pytest


@pytest.mark.asyncio
async def test_notes_require_auth(client):
    resp = await client.get("/api/v1/notes")
    assert resp.status_code == 401
