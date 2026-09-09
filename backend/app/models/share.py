"""文章分享/转发记录（§4.4，用于统计）。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.mysql import Base


class ArticleShare(Base):
    __tablename__ = "article_shares"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("articles.id"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True, index=True
    )
    platform: Mapped[str] = mapped_column(String(20), default="link")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
