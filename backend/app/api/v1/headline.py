"""
Headline Generation API endpoints.

POST /generate    — Generate headline(s) from article text
GET  /history     — Paginated generation history
GET  /{id}        — Single generation detail
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.headline_repository import (
    get_generation_by_id,
    get_generations,
)
from app.schemas.headline import (
    EntityInfo,
    HeadlineCandidate,
    HeadlineGenerateRequest,
    HeadlineGenerateResponse,
    HeadlineHistoryResponse,
    PipelineStageLog,
    SemanticExtraction,
    ValidationMetrics,
)
from app.services.headline.headline_service import generate_headline_pipeline

router = APIRouter(prefix="/headline", tags=["Headline"])


@router.post("/generate", response_model=HeadlineGenerateResponse)
async def headline_generate_endpoint(
    payload: HeadlineGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate Sinhala news headlines from an article.

    Runs the full multi-stage pipeline:
      1. Preprocessing
      2. Entity extraction
      3. Style-conditioned generation
      4. Optimization
      5. Validation (with auto-regeneration)
      6. Semantic extraction

    Returns the best headline, all candidates with metrics,
    and a detailed pipeline execution log.
    """
    result = await generate_headline_pipeline(
        article_text=payload.article_text,
        style=payload.style,
        max_length=payload.max_length,
        num_candidates=payload.num_candidates,
        db=db,
    )
    return result


@router.get("/history", response_model=HeadlineHistoryResponse)
async def headline_history_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve paginated headline generation history, newest first.
    """
    records, total = await get_generations(db, page=page, page_size=page_size)

    items = [
        _record_to_response(r) for r in records
    ]

    return HeadlineHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{generation_id}", response_model=HeadlineGenerateResponse)
async def headline_detail_endpoint(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single headline generation by ID.
    """
    record = await get_generation_by_id(db, generation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Generation not found")

    return _record_to_response(record)


def _record_to_response(record) -> HeadlineGenerateResponse:
    """Convert a HeadlineGeneration ORM record to a response schema."""
    return HeadlineGenerateResponse(
        id=str(record.id),
        best_headline=record.best_headline,
        style=record.style,
        candidates=[
            HeadlineCandidate(
                headline=c["headline"],
                rank=c["rank"],
                metrics=ValidationMetrics(**c["metrics"]),
                passed_validation=c["passed_validation"],
            )
            for c in (record.candidates or [])
        ],
        source_entities=[
            EntityInfo(**e) for e in (record.source_entities or [])
        ],
        semantic_extraction=SemanticExtraction(
            **(record.semantic_extraction or {})
        ),
        pipeline_log=[
            PipelineStageLog(**p) for p in (record.pipeline_log or [])
        ],
        regeneration_count=record.regeneration_count,
        created_at=record.created_at,
    )
