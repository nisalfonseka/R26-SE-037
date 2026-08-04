"""
Data access layer for headline generation records.
All database queries for the headline feature go here.
"""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.headline import HeadlineGeneration


async def save_generation(
    db: AsyncSession,
    generation: HeadlineGeneration,
) -> HeadlineGeneration:
    """Insert a new headline generation record and return it with generated fields."""
    db.add(generation)
    await db.flush()
    await db.refresh(generation)
    return generation


async def get_generation_by_id(
    db: AsyncSession,
    generation_id: UUID,
) -> HeadlineGeneration | None:
    """Fetch a single headline generation by its UUID."""
    stmt = select(HeadlineGeneration).where(HeadlineGeneration.id == generation_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_generations(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[HeadlineGeneration], int]:
    """
    Fetch paginated headline generation history, ordered by newest first.

    Returns:
        (list_of_records, total_count)
    """
    # Total count
    count_stmt = select(func.count()).select_from(HeadlineGeneration)
    total = (await db.execute(count_stmt)).scalar() or 0

    # Paginated results
    offset = (page - 1) * page_size
    stmt = (
        select(HeadlineGeneration)
        .order_by(HeadlineGeneration.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    records = list(result.scalars().all())

    return records, total
