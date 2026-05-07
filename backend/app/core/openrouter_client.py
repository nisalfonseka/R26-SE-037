"""
Shared async OpenRouter client.

All services call `openrouter_chat()` to get LLM completions.
The model and API key are loaded from settings, so swapping the model
only requires an .env change — no code changes needed.

OpenRouter is API-compatible with OpenAI's Chat Completions endpoint:
  POST https://openrouter.ai/api/v1/chat/completions
"""

import httpx

from app.core.config import get_settings

_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
_TIMEOUT = 60.0  # seconds


async def openrouter_chat(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """
    Send a chat completion request to OpenRouter and return the text response.

    Args:
        messages:    List of {"role": "...", "content": "..."} dicts.
        model:       Override the default model from settings.
        temperature: Sampling temperature (lower = more deterministic).
        max_tokens:  Maximum output tokens.

    Returns:
        The assistant's reply as a plain string.

    Raises:
        httpx.HTTPStatusError: on non-2xx responses.
        ValueError: if the response has no content.
    """
    settings = get_settings()
    chosen_model = model or settings.OPENROUTER_MODEL

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sinai.local",   # identifies the app to OpenRouter
        "X-Title": "SinAI - Sinhala Journalism LLM",
    }

    payload = {
        "model": chosen_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(
            f"{_OPENROUTER_BASE}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise ValueError(f"Unexpected OpenRouter response shape: {data}") from exc
