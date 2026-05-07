"""
Style Rewriter API endpoints.

POST /rewrite — Rewrite text in target style
GET  /history  — Paginated rewrite history
GET  /{id}     — Single rewrite detail
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.style import StyleRewrite
from app.repositories.style_repository import (
    get_rewrite_by_id,
    get_rewrites,
    save_rewrite,
)
from app.schemas.style import (
    StyleHistoryResponse,
    StyleRewriteRequest,
    StyleRewriteResponse,
)
from app.services.style.style_service import rewrite_style

router = APIRouter(prefix="/style", tags=["Style"])


@router.post("/rewrite", response_model=StyleRewriteResponse)
async def style_rewrite_endpoint(
    payload: StyleRewriteRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Rewrite Sinhala text in the specified journalistic style.
    """
    result = await rewrite_style(payload.text, payload.tone, db)
    return result


@router.get("/history", response_model=StyleHistoryResponse)
async def style_history_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve paginated style rewrite history, newest first.
    """
    records, total = await get_rewrites(db, page=page, page_size=page_size)

    items = [
        StyleRewriteResponse(
            id=str(r.id),
            original=r.original_text,
            rewritten=r.rewritten_text,
            tone=r.target_style,
            created_at=r.created_at,
        )
        for r in records
    ]

    return StyleHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{rewrite_id}", response_model=StyleRewriteResponse)
async def style_detail_endpoint(
    rewrite_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single style rewrite by ID.
    """
    record = await get_rewrite_by_id(db, rewrite_id)
    if not record:
        raise HTTPException(status_code=404, detail="Rewrite not found")

    return StyleRewriteResponse(
        id=str(record.id),
        original=record.original_text,
        rewritten=record.rewritten_text,
        tone=record.target_style,
        created_at=record.created_at,
    )