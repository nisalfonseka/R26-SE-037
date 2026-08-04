"""
Data access layer for summarization records.
"""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.summarization import Summarization


async def save_summarization(
    db: AsyncSession,
    record: Summarization,
) -> Summarization:
    """Insert a new summarization record and return it with generated fields."""
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_summarization_by_id(
    db: AsyncSession,
    record_id: UUID,
) -> Summarization | None:
    """Fetch a single summarization by UUID."""
    stmt = select(Summarization).where(Summarization.id == record_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_summarizations(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Summarization], int]:
    """Fetch paginated summarization history, newest first."""
    count_stmt = select(func.count()).select_from(Summarization)
    total = (await db.execute(count_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    stmt = (
        select(Summarization)
        .order_by(Summarization.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), total
