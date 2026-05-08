"""
Grammar checking service — powered by OpenRouter LLM.

Sends Sinhala text to the LLM with a structured prompt that instructs it to:
  1. Correct grammatical errors
  2. Return a JSON object with the corrected text and a list of corrections

The response is parsed, persisted to PostgreSQL, and returned.
"""

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.openrouter_client import openrouter_chat
from app.models.grammar import GrammarCorrection
from app.repositories.grammar_repository import save_correction
from app.schemas.grammar import CorrectionDetail, GrammarCheckResponse

logger = logging.getLogger(__name__)

# ── System prompt ──
_SYSTEM_PROMPT = """You are an expert Sinhala language editor and grammar checker.
Your task is to correct grammatical errors in the given Sinhala text.

You MUST respond with a valid JSON object in exactly this format (no markdown, no extra text):
{
  "corrected": "<full corrected text>",
  "corrections": [
    {
      "position": <integer character offset in original>,
      "original": "<original incorrect fragment>",
      "corrected": "<corrected fragment>",
      "rule": "<brief description of the grammar rule applied>"
    }
  ]
}

Rules:
- Fix verb endings (e.g., යනව → යනවා)
- Fix particle and postposition errors
- Fix spelling mistakes
- Fix spacing and punctuation
- If the text has no errors, return the original text unchanged with an empty corrections array
- Always return valid JSON, nothing else"""


async def check_grammar(text: str, db: AsyncSession) -> GrammarCheckResponse:
    """
    Check Sinhala text for grammar errors using the OpenRouter LLM.

    Args:
        text: Raw Sinhala text from the user.
        db:   Async database session.

    Returns:
        GrammarCheckResponse with corrected text and correction details.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": f"Please check and correct the following Sinhala text:\n\n{text}"},
    ]

    raw_response = await openrouter_chat(messages, temperature=0.1, max_tokens=4096)

    # Parse JSON response
    corrected_text, corrections = _parse_response(raw_response, fallback_text=text)

    # Persist to database
    record = GrammarCorrection(
        original_text=text,
        corrected_text=corrected_text,
        corrections=[c.model_dump() for c in corrections],
        correction_count=len(corrections),
    )
    saved = await save_correction(db, record)

    return GrammarCheckResponse(
        id=str(saved.id),
        corrected=saved.corrected_text,
        corrections=corrections,
        correction_count=saved.correction_count,
        created_at=saved.created_at,
    )


def _parse_response(
    raw: str,
    fallback_text: str,
) -> tuple[str, list[CorrectionDetail]]:
    """
    Parse the LLM's JSON response into corrected text and correction details.
    Falls back gracefully if the LLM returns malformed output.
    """
    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned

    try:
        data = json.loads(cleaned)
        corrected = data.get("corrected", fallback_text)
        raw_corrections = data.get("corrections", [])

        corrections = []
        for c in raw_corrections:
            try:
                corrections.append(CorrectionDetail(
                    position=int(c.get("position", 0)),
                    original=str(c.get("original", "")),
                    corrected=str(c.get("corrected", "")),
                    rule=str(c.get("rule", "")),
                ))
            except Exception:
                continue  # skip malformed individual corrections

        return corrected, corrections

    except (json.JSONDecodeError, AttributeError):
        logger.warning("Grammar service: failed to parse LLM JSON response, returning raw text")
        return fallback_text, []