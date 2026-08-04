"""
News summarization service — powered by OpenRouter LLM.

Summarizes long Sinhala news articles into concise summaries
at the requested length (short / medium / long).
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.openrouter_client import openrouter_chat
from app.models.summarization import Summarization
from app.repositories.summarization_repository import save_summarization
from app.schemas.summarization import SummarizeResponse

logger = logging.getLogger(__name__)

# ── Length instructions ──
_LENGTH_INSTRUCTIONS = {
    "short": "Write a very concise summary in 1–2 sentences only.",
    "medium": "Write a clear summary in one well-structured paragraph (4–6 sentences).",
    "long": "Write a comprehensive summary in 3 paragraphs covering the main points, key details, and conclusion.",
}

_SYSTEM_PROMPT = """You are an expert Sinhala news editor specialising in summarization.
Your task is to summarize the given Sinhala news article.

Guidelines:
- Write the summary in Sinhala (not English)
- Preserve factual accuracy — do not add or invent information
- Use clear, journalistic Sinhala prose
- Follow the specified length instruction exactly
- Return ONLY the summary text, no preamble, no JSON, no labels"""


async def summarize_article(
    text: str,
    length: str,
    db: AsyncSession,
) -> SummarizeResponse:
    """
    Summarize a Sinhala news article using the OpenRouter LLM.

    Args:
        text:   The full article text.
        length: Desired summary length — "short", "medium", or "long".
        db:     Async database session.

    Returns:
        SummarizeResponse with the generated summary.
    """
    length_instruction = _LENGTH_INSTRUCTIONS.get(length, _LENGTH_INSTRUCTIONS["medium"])

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"{length_instruction}\n\n"
                f"Article to summarize:\n\n{text}"
            ),
        },
    ]

    # Higher temperature for more natural prose; longer max_tokens for "long" mode
    max_tokens = {"short": 256, "medium": 512, "long": 1024}.get(length, 512)
    summary = await openrouter_chat(messages, temperature=0.4, max_tokens=max_tokens)

    # Persist to database
    record = Summarization(
        original_text=text,
        summary=summary,
        length_preference=length,
    )
    saved = await save_summarization(db, record)

    return SummarizeResponse(
        id=str(saved.id),
        summary=saved.summary,
        length=saved.length_preference,
        created_at=saved.created_at,
    )