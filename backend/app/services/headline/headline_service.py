"""
Headline generation pipeline orchestrator.

Coordinates all pipeline stages:
  1. Preprocessing (clean + tokenize)
  2. Entity extraction
  3. Style conditioning
  4. Headline generation (candidates)
  5. Headline optimization
  6. Validation (with regeneration loop)
  7. Semantic extraction
  8. Persist to database

Each stage is timed and logged in the pipeline execution log.
"""

import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.preprocessing.cleaner import clean_text
from app.models.headline import HeadlineGeneration
from app.repositories.headline_repository import save_generation
from app.schemas.headline import (
    HeadlineStyle,
    HeadlineCandidate,
    HeadlineGenerateResponse,
    PipelineStageLog,
    ValidationMetrics,
)
from app.services.headline.entity_extractor import extract_entities
from app.services.headline.headline_generator import generate_candidates
from app.services.headline.headline_optimizer import optimize_headline
from app.services.headline.headline_validator import (
    validate_headline,
    passes_thresholds,
)
from app.services.headline.semantic_extractor import extract_semantics


# ── Pipeline configuration ──
MAX_REGENERATION_ATTEMPTS = 3


async def generate_headline_pipeline(
    article_text: str,
    style: HeadlineStyle,
    max_length: int,
    num_candidates: int,
    db: AsyncSession,
) -> HeadlineGenerateResponse:
    """
    Execute the full headline generation pipeline.

    Args:
        article_text:   Raw Sinhala news article text.
        style:          Desired headline style.
        max_length:     Maximum headline character length.
        num_candidates: Number of headline candidates.
        db:             Async database session.

    Returns:
        HeadlineGenerateResponse with best headline, candidates, and metrics.
    """
    pipeline_log: list[PipelineStageLog] = []
    regeneration_count = 0

    # ── Stage 1: Preprocessing ──
    t0 = time.perf_counter()
    cleaned = clean_text(article_text)
    pipeline_log.append(_log("preprocessing", t0, "Text cleaned and normalized"))

    # ── Stage 2: Entity Extraction ──
    t0 = time.perf_counter()
    source_entities = extract_entities(cleaned)
    pipeline_log.append(_log(
        "entity_extraction", t0,
        f"Extracted {len(source_entities)} entities",
    ))

    # ── Stage 3–6: Generate → Optimize → Validate (with regen loop) ──
    all_candidates: list[HeadlineCandidate] = []
    best_headline = ""

    for attempt in range(MAX_REGENERATION_ATTEMPTS + 1):
        # Stage 3: Style-conditioned generation
        t0 = time.perf_counter()
        raw_headlines = generate_candidates(
            cleaned, source_entities, style, max_length, num_candidates,
        )
        pipeline_log.append(_log(
            "generation", t0,
            f"Attempt {attempt + 1}: generated {len(raw_headlines)} candidates",
        ))

        # Stage 4: Optimization
        t0 = time.perf_counter()
        optimized = [
            optimize_headline(h, style, max_length)
            for h in raw_headlines
        ]
        pipeline_log.append(_log("optimization", t0, "Headlines optimized"))

        # Stage 5: Validation
        t0 = time.perf_counter()
        candidates_this_round: list[HeadlineCandidate] = []
        for h in optimized:
            metrics = validate_headline(h, cleaned, source_entities, max_length)
            passed = passes_thresholds(metrics)
            candidates_this_round.append(HeadlineCandidate(
                headline=h,
                rank=0,  # ranked later
                metrics=metrics,
                passed_validation=passed,
            ))

        pipeline_log.append(_log(
            "validation", t0,
            f"{sum(1 for c in candidates_this_round if c.passed_validation)}"
            f"/{len(candidates_this_round)} passed thresholds",
        ))

        all_candidates.extend(candidates_this_round)

        # Check if any passed
        passing = [c for c in all_candidates if c.passed_validation]
        if passing:
            break

        # Otherwise, trigger regeneration
        if attempt < MAX_REGENERATION_ATTEMPTS:
            regeneration_count += 1
            pipeline_log.append(_log(
                "regeneration", time.perf_counter(),
                f"Regeneration triggered (attempt {regeneration_count})",
                status="warning",
            ))

    # ── Rank candidates ──
    all_candidates.sort(
        key=lambda c: (
            c.passed_validation,
            c.metrics.rouge_1 + c.metrics.semantic_similarity + c.metrics.entity_coverage,
        ),
        reverse=True,
    )
    for i, c in enumerate(all_candidates):
        c.rank = i + 1

    best = all_candidates[0] if all_candidates else None
    best_headline = best.headline if best else cleaned[:max_length]

    # ── Stage 7: Semantic Extraction ──
    t0 = time.perf_counter()
    semantics = extract_semantics(best_headline, cleaned)
    pipeline_log.append(_log(
        "semantic_extraction", t0,
        f"Extracted {len(semantics.key_themes)} themes",
    ))

    # ── Stage 8: Persist to database ──
    t0 = time.perf_counter()
    record = HeadlineGeneration(
        article_text=article_text,
        style=style.value,
        max_length=max_length,
        best_headline=best_headline,
        candidates=[c.model_dump() for c in all_candidates],
        source_entities=[e.model_dump() for e in source_entities],
        semantic_extraction=semantics.model_dump(),
        pipeline_log=[p.model_dump() for p in pipeline_log],
        regeneration_count=regeneration_count,
    )
    saved = await save_generation(db, record)
    pipeline_log.append(_log("persistence", t0, "Saved to database"))

    return HeadlineGenerateResponse(
        id=str(saved.id),
        best_headline=best_headline,
        style=style,
        candidates=all_candidates,
        source_entities=source_entities,
        semantic_extraction=semantics,
        pipeline_log=pipeline_log,
        regeneration_count=regeneration_count,
        created_at=saved.created_at,
    )


def _log(
    stage: str,
    start_time: float,
    message: str = "",
    status: str = "success",
) -> PipelineStageLog:
    """Create a pipeline stage log entry."""
    duration_ms = (time.perf_counter() - start_time) * 1000
    return PipelineStageLog(
        stage=stage,
        status=status,
        duration_ms=round(duration_ms, 2),
        message=message,
    )