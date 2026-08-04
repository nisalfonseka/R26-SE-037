"""
News Summarizer API endpoints.

POST /check   — Summarize an article
GET  /history — Paginated summarization history
GET  /{id}    — Single summarization detail
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.summarization_repository import (
    get_summarization_by_id,
    get_summarizations,
)
from app.schemas.summarization import (
    SummarizeHistoryResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.services.summarizer.summarizer_service import summarize_article

router = APIRouter(prefix="/summarize", tags=["Summarizer"])


@router.post("/check", response_model=SummarizeResponse)
async def summarize_endpoint(
    payload: SummarizeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Summarize a Sinhala news article.

    Accepts the full article text and a desired length preference
    (short / medium / long). Returns the summary in Sinhala.
    """
    return await summarize_article(payload.text, payload.length, db)


@router.get("/history", response_model=SummarizeHistoryResponse)
async def summarize_history_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve paginated summarization history, newest first."""
    records, total = await get_summarizations(db, page=page, page_size=page_size)

    items = [
        SummarizeResponse(
            id=str(r.id),
            summary=r.summary,
            length=r.length_preference,
            created_at=r.created_at,
        )
        for r in records
    ]

    return SummarizeHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{record_id}", response_model=SummarizeResponse)
async def summarize_detail_endpoint(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a single summarization by ID."""
    record = await get_summarization_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Summarization not found")

    return SummarizeResponse(
        id=str(record.id),
        summary=record.summary,
        length=record.length_preference,
        created_at=record.created_at,
    )
