"""文章模型（§4.1.3 articles 表）与文章-标签关联表（§4.1.7 article_tags）。"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.mysql import Base

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("article_id", BigInteger, ForeignKey("articles.id"), nullable=False, index=True),
    Column("tag_id", BigInteger, ForeignKey("tags.id"), nullable=False, index=True),
    UniqueConstraint("article_id", "tag_id", name="uk_article_tag"),
)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), default="")
    content_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    cover_image: Mapped[str] = mapped_column(String(255), default="")
    category_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(SmallInteger, default=0)  # 0-草稿 1-已发布 2-已下架
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    tags = relationship("Tag", secondary=article_tags, lazy="selectin")
