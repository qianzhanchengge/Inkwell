"""文章接口测试骨架。"""
import pytest


def test_article_routes_registered():
    """确认文章相关路由已注册（无需连接数据库）。"""
    from app.main import app

    paths = [route.path for route in app.routes]
    assert "/api/v1/articles" in paths
    assert "/api/v1/articles/mine" in paths
    assert "/api/v1/articles/search" in paths
