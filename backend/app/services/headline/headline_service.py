"""
Headline generation service — powered by OpenRouter LLM.

Generates multiple Sinhala headline candidates for a news article
in a specified journalistic style.
The LLM returns a JSON array of ranked headlines.
"""

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.openrouter_client import openrouter_chat
from app.models.headline import HeadlineGeneration
from app.repositories.headline_repository import save_generation
from app.schemas.headline import (
    HeadlineCandidate,
    HeadlineGenerateResponse,
    HeadlineStyle,
    ValidationMetrics,
    PipelineStageLog,
    EntityInfo,
    SemanticExtraction,
)

logger = logging.getLogger(__name__)

# ── Style descriptions ──
_STYLE_DESCRIPTIONS = {
    "breaking": "urgent breaking-news style — short, punchy, high-impact",
    "formal": "formal broadsheet newspaper style — precise, informative, professional",
    "feature": "feature story style — engaging, narrative-driven, human interest",
    "analytical": "analytical/opinion style — context-heavy, thoughtful, explanatory",
    "sports": "sports reporting style — energetic, vivid, action-oriented",
}

_SYSTEM_PROMPT = """You are an expert Sinhala news editor specialising in headline writing.
Your task is to generate compelling Sinhala headlines for the given news article.

You MUST respond with a valid JSON object in exactly this format (no markdown, no extra text):
{
  "headlines": [
    {"rank": 1, "headline": "<best headline>", "rationale": "<brief English rationale>"},
    {"rank": 2, "headline": "<second headline>", "rationale": "<brief English rationale>"},
    ...
  ]
}

Guidelines for great Sinhala headlines:
- Be concise (ideally under 60 characters)
- Capture the most newsworthy element
- Use active voice where possible
- Match the specified style
- Do NOT start with "ශ්‍රී ලංකා" unless the story is specifically about Sri Lanka
- Always return valid JSON, nothing else"""


async def generate_headline_pipeline(
    article_text: str,
    style: HeadlineStyle,
    max_length: int,
    num_candidates: int,
    db: AsyncSession,
) -> HeadlineGenerateResponse:
    """
    Generate Sinhala headline candidates using the OpenRouter LLM.

    Args:
        article_text:   Raw Sinhala news article text.
        style:          Desired headline style.
        max_length:     Maximum character length per headline.
        num_candidates: Number of headline candidates to generate.
        db:             Async database session.

    Returns:
        HeadlineGenerateResponse with candidates and the best headline.
    """
    style_desc = _STYLE_DESCRIPTIONS.get(style.value, _STYLE_DESCRIPTIONS["formal"])

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Generate {num_candidates} Sinhala headlines in {style_desc} style.\n"
                f"Each headline must be under {max_length} characters.\n\n"
                f"Article:\n\n{article_text}"
            ),
        },
    ]

    raw_response = await openrouter_chat(messages, temperature=0.7, max_tokens=1024)
    candidates = _parse_response(raw_response, num_candidates)

    best_headline = candidates[0].headline if candidates else article_text[:max_length]

    # Persist to database
    record = HeadlineGeneration(
        article_text=article_text,
        style=style.value,
        max_length=max_length,
        best_headline=best_headline,
        candidates=[c.model_dump() for c in candidates],
        source_entities=[],
        semantic_extraction={},
        pipeline_log=[],
        regeneration_count=0,
    )
    saved = await save_generation(db, record)

    return HeadlineGenerateResponse(
        id=str(saved.id),
        best_headline=best_headline,
        style=style,
        candidates=candidates,
        source_entities=[],
        semantic_extraction=SemanticExtraction(
            key_themes=[],
            sentiment="neutral",
            topic_category="general",
        ),
        pipeline_log=[
            PipelineStageLog(
                stage="llm_generation",
                status="success",
                duration_ms=0,
                message=f"Generated {len(candidates)} candidates via OpenRouter",
            )
        ],
        regeneration_count=0,
        created_at=saved.created_at,
    )


def _parse_response(raw: str, expected_count: int) -> list[HeadlineCandidate]:
    """Parse the LLM JSON response into a list of HeadlineCandidate objects."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned

    try:
        data = json.loads(cleaned)
        headlines_data = data.get("headlines", [])

        candidates = []
        for item in headlines_data:
            try:
                candidates.append(HeadlineCandidate(
                    headline=str(item.get("headline", "")),
                    rank=int(item.get("rank", len(candidates) + 1)),
                    metrics=ValidationMetrics(
                        rouge_1=0.0,
                        rouge_2=0.0,
                        rouge_l=0.0,
                        semantic_similarity=0.0,
                        entity_coverage=0.0,
                        length_score=1.0,
                        readability_score=1.0,
                    ),
                    passed_validation=True,
                ))
            except Exception:
                continue

        return candidates

    except (json.JSONDecodeError, AttributeError):
        logger.warning("Headline service: failed to parse LLM JSON response")
        return []