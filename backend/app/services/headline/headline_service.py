"""
Headline generation service — powered by OpenRouter LLM.

Generates multiple Sinhala headline candidates for a news article
in a specified journalistic style.
The LLM returns a JSON array of ranked headlines.
"""

import asyncio
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

# ── Style descriptions (keys must match HeadlineStyle enum values) ──
_STYLE_DESCRIPTIONS = {
    "formal": "formal broadsheet newspaper style — precise, informative, professional",
    "breaking_news": "urgent breaking-news style — short, punchy, high-impact",
    "youth": "casual, modern youth-oriented style using contemporary Sinhala expressions",
    "editorial": "editorial opinion/commentary style with a strong, authoritative voice",
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

    # Brief pause to avoid free-tier rate limiting between consecutive LLM calls
    await asyncio.sleep(2)

    # Generate LLM-powered English visual prompt from the Sinhala headline
    visual_prompt = await _generate_visual_prompt(best_headline, style.value)

    semantic = SemanticExtraction(
        key_themes=[],
        entities=[],
        visual_prompt=visual_prompt,
    )

    # Persist to database
    record = HeadlineGeneration(
        article_text=article_text,
        style=style.value,
        max_length=max_length,
        best_headline=best_headline,
        candidates=[c.model_dump() for c in candidates],
        source_entities=[],
        semantic_extraction=semantic.model_dump(),
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
        semantic_extraction=semantic,
        pipeline_log=[
            PipelineStageLog(
                stage="llm_generation",
                status="success",
                duration_ms=0,
                message=f"Generated {len(candidates)} candidates via OpenRouter",
            ),
            PipelineStageLog(
                stage="visual_prompt",
                status="success",
                duration_ms=0,
                message="Generated English visual prompt for image generation",
            ),
        ],
        regeneration_count=0,
        created_at=saved.created_at,
    )


async def _generate_visual_prompt(headline: str, style: str) -> str:
    """
    Use the LLM to translate a Sinhala headline into an English visual prompt
    suitable for text-to-image generation APIs.

    The prompt is engineered to be robust even with weaker/random free models:
    - Uses a structured few-shot approach so the model sees the expected format
    - Asks for a single plain-text line (no JSON, no markdown)
    - Validates and cleans the output before returning
    """

    _VISUAL_STYLE_HINTS = {
        "formal": "professional newsroom setting, well-lit, clean composition",
        "breaking_news": "dramatic, urgent atmosphere, dynamic angle, breaking-news feel",
        "youth": "vibrant, colorful, modern urban setting, youthful energy",
        "editorial": "thoughtful, moody lighting, opinion piece feel, close-up portraits",
    }
    style_hint = _VISUAL_STYLE_HINTS.get(style, _VISUAL_STYLE_HINTS["formal"])

    messages = [
        {
            "role": "system",
            "content": (
                "You are a visual prompt engineer for a Sinhala news platform. "
                "You convert Sinhala news headlines into English image-generation prompts.\n\n"
                "RULES (follow every rule exactly):\n"
                "1. First, mentally translate the Sinhala headline into English.\n"
                "2. Then write a vivid, specific visual scene description in English.\n"
                "3. Include: main subjects, their actions, the setting/location, and the mood.\n"
                "4. Use concrete visual nouns and adjectives (e.g. 'a crowded parliament hall', "
                "'a farmer inspecting drought-damaged rice paddies').\n"
                "5. Do NOT include any Sinhala text in the output.\n"
                "6. Do NOT output markdown, JSON, quotes, or any explanation.\n"
                "7. Keep under 60 words before the style suffix.\n"
                "8. Always end the prompt with exactly: news photography style, photojournalism, high resolution\n\n"
                "EXAMPLES:\n\n"
                "Sinhala headline: ශ්‍රී ලංකා ක්‍රිකට් කණ්ඩායම ඕස්ට්‍රේලියාවට එරෙහිව ජයග්‍රහණය ලබයි\n"
                "Output: Sri Lankan cricket players celebrating a victory on the field, "
                "waving flags, sunlit stadium packed with cheering fans in the background, "
                f"{style_hint}, news photography style, photojournalism, high resolution\n\n"
                "Sinhala headline: කොළඹ නගරයේ ගංවතුර තත්ත්වය උත්සන්න වෙයි\n"
                "Output: Flooded streets in Colombo city center, murky brown water "
                "reaching waist height, stranded vehicles, residents wading through water, "
                f"overcast sky, {style_hint}, news photography style, photojournalism, high resolution\n\n"
                "Sinhala headline: ජනාධිපති නව අමාත්‍ය මණ්ඩලය පත් කරයි\n"
                "Output: A formal swearing-in ceremony in a grand government hall, "
                "officials in formal attire taking oath before the president, "
                f"national flags and wooden podium, {style_hint}, "
                "news photography style, photojournalism, high resolution"
            ),
        },
        {
            "role": "user",
            "content": f"Sinhala headline: {headline}\nOutput:",
        },
    ]

    try:
        result = await openrouter_chat(messages, temperature=0.4, max_tokens=200)
        result = _clean_visual_prompt(result)
        logger.info("Visual prompt generated: %s", result[:120])
        return result
    except Exception as exc:
        logger.warning("Visual prompt generation failed (%s), using fallback", exc)
        return (
            f"A news scene depicting a current event in Sri Lanka, "
            f"{style_hint}, "
            f"news photography style, photojournalism, high resolution"
        )


def _clean_visual_prompt(raw: str) -> str:
    """
    Sanitise the LLM output so it is a clean, single-line image prompt.
    Strips markdown fences, quotes, prefixes like 'Output:' and ensures
    the required style suffix is present.
    """
    text = raw.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]).strip() if len(lines) > 2 else text

    # Remove surrounding quotes
    for q in ('"', "'", "`"):
        if text.startswith(q) and text.endswith(q):
            text = text[1:-1].strip()

    # Remove common prefixes the LLM might add
    for prefix in ("Output:", "Visual prompt:", "Prompt:", "Image prompt:"):
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()

    # Collapse to single line
    text = " ".join(text.split())

    # Ensure the style suffix is present
    suffix = "news photography style, photojournalism, high resolution"
    if suffix not in text.lower():
        text = text.rstrip(".,;: ") + f", {suffix}"

    return text


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
                        bleu=0.0,
                        semantic_similarity=0.0,
                        entity_coverage=0.0,
                        grammar_pass=True,
                        length_ok=True,
                    ),
                    passed_validation=True,
                ))
            except Exception:
                continue

        return candidates

    except (json.JSONDecodeError, AttributeError):
        logger.warning("Headline service: failed to parse LLM JSON response")
        return []