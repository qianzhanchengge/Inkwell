"""笔记模型（§4.1.2 notes 表）与笔记-标签关联表（§4.1.6 note_tags）。"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.mysql import Base

note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("note_id", BigInteger, nullable=False, index=True),
    Column("tag_id", BigInteger, nullable=False, index=True),
    UniqueConstraint("note_id", "tag_id", name="uk_note_tag"),
)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    is_pinned: Mapped[int] = mapped_column(SmallInteger, default=0)  # 0-否 1-是
    status: Mapped[int] = mapped_column(SmallInteger, default=1)  # 0-删除 1-正常
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    tags = relationship("Tag", secondary=note_tags, lazy="selectin")
