"""分类业务逻辑。"""
from typing import List

from sqlalchemy import select

from app.core.exceptions import NotFoundException
from app.database.mysql import get_session_factory
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def list_categories(user_id: int, type_: int | None = None) -> List[Category]:
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(Category).where(Category.user_id == user_id)
        if type_ is not None:
            stmt = stmt.where(Category.type == type_)
        stmt = stmt.order_by(Category.sort_order, Category.id)
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def create_category(user_id: int, data: CategoryCreate) -> Category:
    factory = get_session_factory()
    async with factory() as session:
        category = Category(
            user_id=user_id, name=data.name, type=data.type, sort_order=data.sort_order
        )
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category


async def update_category(user_id: int, category_id: int, data: CategoryUpdate) -> Category:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id, Category.user_id == user_id)
        )
        category = result.scalar_one_or_none()
        if category is None:
            raise NotFoundException("分类不存在")

        if data.name is not None:
            category.name = data.name
        if data.sort_order is not None:
            category.sort_order = data.sort_order

        await session.commit()
        await session.refresh(category)
        return category


async def delete_category(user_id: int, category_id: int) -> None:
    """删除分类；删除前把其下笔记/文章的分类引用置空（避免悬空外键）。"""
    from sqlalchemy import update

    from app.models.article import Article
    from app.models.note import Note

    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id, Category.user_id == user_id)
        )
        category = result.scalar_one_or_none()
        if category is None:
            raise NotFoundException("分类不存在")

        await session.execute(
            update(Note)
            .where(Note.category_id == category_id, Note.user_id == user_id)
            .values(category_id=None)
        )
        await session.execute(
            update(Article)
            .where(Article.category_id == category_id, Article.user_id == user_id)
            .values(category_id=None)
        )

        await session.delete(category)
        await session.commit()
