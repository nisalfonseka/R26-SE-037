"""
Style rewriting service — powered by OpenRouter LLM.

Rewrites Sinhala text in a specified journalistic style.
The LLM is given a style-specific system prompt and returns JSON.
"""

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.openrouter_client import openrouter_chat
from app.models.style import StyleRewrite
from app.repositories.style_repository import save_rewrite
from app.schemas.style import StyleRewriteResponse

logger = logging.getLogger(__name__)

# ── Style descriptions for the prompt ──
_STYLE_DESCRIPTIONS = {
    "formal": "formal, professional journalistic Sinhala suitable for a broadsheet newspaper",
    "editorial": "editorial opinion/commentary style with a strong, authoritative voice",
    "sports": "energetic, fast-paced sports reporting style with vivid action language",
    "youth": "casual, modern youth-oriented style using contemporary Sinhala expressions",
    "children": "simple, friendly, easy-to-understand style suitable for children aged 8–12",
    "breaking": "urgent, concise breaking-news style emphasising immediacy and impact",
}

_SYSTEM_PROMPT = """You are an expert Sinhala language writer and editor specialising in journalism.
Your task is to rewrite the given Sinhala text in the specified journalistic style.

You MUST respond with a valid JSON object in exactly this format (no markdown, no extra text):
{
  "rewritten": "<the rewritten text in the target style>",
  "changes_summary": "<brief English description of the main stylistic changes made>"
}

Guidelines:
- Preserve the factual content and meaning of the original text
- Adapt vocabulary, sentence structure, and tone to match the target style
- Do not add or remove key facts
- Always return valid JSON, nothing else"""


async def rewrite_style(
    text: str,
    tone: str,
    db: AsyncSession,
) -> StyleRewriteResponse:
    """
    Rewrite Sinhala text in the specified journalistic style using OpenRouter LLM.

    Args:
        text: Original Sinhala text.
        tone: Target style key (formal, editorial, sports, youth, children, breaking).
        db:   Async database session.

    Returns:
        StyleRewriteResponse with the rewritten text.
    """
    style_desc = _STYLE_DESCRIPTIONS.get(tone, _STYLE_DESCRIPTIONS["formal"])

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Please rewrite the following Sinhala text in {style_desc} style:\n\n{text}"
            ),
        },
    ]

    raw_response = await openrouter_chat(messages, temperature=0.6, max_tokens=4096)
    rewritten_text, changes_summary = _parse_response(raw_response, fallback_text=text)

    # Persist to database
    record = StyleRewrite(
        original_text=text,
        rewritten_text=rewritten_text,
        target_style=tone,
    )
    saved = await save_rewrite(db, record)

    return StyleRewriteResponse(
        id=str(saved.id),
        original=saved.original_text,
        rewritten=saved.rewritten_text,
        tone=saved.target_style,
        created_at=saved.created_at,
    )


def _parse_response(raw: str, fallback_text: str) -> tuple[str, str]:
    """Parse the LLM JSON response. Returns (rewritten_text, changes_summary)."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned

    try:
        data = json.loads(cleaned)
        return (
            data.get("rewritten", fallback_text),
            data.get("changes_summary", ""),
        )
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Style service: failed to parse LLM JSON, returning raw response")
        # If the whole response looks like plain text rewriting, use it directly
        return cleaned if cleaned else fallback_text, ""