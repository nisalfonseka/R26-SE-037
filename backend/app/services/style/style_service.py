"""
Style rewriting service.

Calls fine-tuned SinLlama model for style-controlled Sinhala text generation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.style import StyleRewrite
from app.repositories.style_repository import save_rewrite
from app.schemas.style import StyleRewriteResponse


# Style prompt templates
STYLE_PROMPTS = {
    "formal": "Rewrite the following Sinhala text in formal journalistic style:\n\n{text}\n\nRewritten:",
    "editorial": "Rewrite the following Sinhala text in editorial commentary style:\n\n{text}\n\nRewritten:",
    "sports": "Rewrite the following Sinhala text in sports reporting style:\n\n{text}\n\nRewritten:",
    "youth": "Rewrite the following Sinhala text in youth-oriented style:\n\n{text}\n\nRewritten:",
    "children": "Rewrite the following Sinhala text in children-friendly style:\n\n{text}\n\nRewritten:",
    "breaking": "Rewrite the following Sinhala text in breaking news style:\n\n{text}\n\nRewritten:",
}


async def rewrite_style(text: str, tone: str, db: AsyncSession) -> StyleRewriteResponse:
    """
    Rewrite Sinhala text in specified style using SinLlama model.

    Args:
        text: Original Sinhala text.
        tone: Target style (formal, editorial, sports, youth, children, breaking).
        db:   Async database session.

    Returns:
        StyleRewriteResponse with rewritten text.
    """
    # Get prompt template for target style
    prompt_template = STYLE_PROMPTS.get(tone, STYLE_PROMPTS["formal"])
    prompt = prompt_template.format(text=text)

    # TODO: Replace with actual model inference
    # For now, using placeholder - integrate your SinLlama model here
    # Example:
    # from transformers import pipeline
    # generator = pipeline("text2text-generation", model="models/fine_tuned/style_rewriter")
    # rewritten_text = generator(prompt, max_new_tokens=1024)[0]["generated_text"]

    rewritten_text = f"[{tone.upper()} STYLE]: {text}"

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