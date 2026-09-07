"""模型聚合导出：import 本模块即注册全部 ORM 模型到 Base.metadata。"""
from app.models.article import Article, article_tags
from app.models.category import Category
from app.models.note import Note, note_tags
from app.models.tag import Tag
from app.models.user import User

__all__ = [
    "User",
    "Note",
    "Article",
    "Category",
    "Tag",
    "note_tags",
    "article_tags",
]
