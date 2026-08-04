"""
Database operations for style rewrite history.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.style import StyleRewrite


async def save_rewrite(db: AsyncSession, rewrite: StyleRewrite) -> StyleRewrite:
    """Persist a style rewrite record."""
    db.add(rewrite)
    await db.commit()
    await db.refresh(rewrite)
    return rewrite


async def get_rewrites(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[StyleRewrite], int]:
    """Retrieve paginated rewrite history, newest first."""
    offset = (page - 1) * page_size

    count_stmt = select(StyleRewrite)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())

    stmt = (
        select(StyleRewrite)
        .order_by(StyleRewrite.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    return list(records), total


async def get_rewrite_by_id(db: AsyncSession, rewrite_id: UUID) -> StyleRewrite | None:
    """Retrieve a single rewrite by ID."""
    stmt = select(StyleRewrite).where(StyleRewrite.id == rewrite_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()