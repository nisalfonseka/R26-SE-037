"""
Shared async OpenRouter client.

All services call `openrouter_chat()` to get LLM completions.
The model and API key are loaded from settings, so swapping the model
only requires an .env change — no code changes needed.

OpenRouter is API-compatible with OpenAI's Chat Completions endpoint:
  POST https://openrouter.ai/api/v1/chat/completions

Image generation uses ModelsLab API:
  POST https://api.modelslab.com/api/v1/image/text2img
"""

import asyncio
import base64
import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
_TIMEOUT = 60.0  # seconds
_MAX_RETRIES = 3  # retry on 429 before giving up


def _build_headers(settings) -> dict:
    return {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sinai.local",
        "X-Title": "SinAI - Sinhala Journalism LLM",
    }


async def openrouter_chat(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """
    Send a chat completion request to OpenRouter and return the text response.

    Retries up to _MAX_RETRIES times on 429 with exponential backoff.

    Raises:
        httpx.HTTPStatusError: on non-2xx responses after all retries.
        ValueError: if the response has no content.
    """
    settings = get_settings()
    chosen_model = model or settings.OPENROUTER_MODEL
    headers = _build_headers(settings)
    payload = {
        "model": chosen_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.post(
                    f"{_OPENROUTER_BASE}/chat/completions",
                    headers=headers,
                    json=payload,
                )

            # 429 (rate limit) and 402 (free-tier quota exceeded) are retryable
            if response.status_code in (429, 402):
                wait = 2 ** attempt  # 1 s, 2 s, 4 s
                logger.warning(
                    "OpenRouter %d on attempt %d/%d — waiting %ds before retry",
                    response.status_code, attempt + 1, _MAX_RETRIES, wait,
                )
                await asyncio.sleep(wait)
                last_exc = httpx.HTTPStatusError(
                    f"{response.status_code} {response.reason_phrase}",
                    request=response.request, response=response,
                )
                continue

            response.raise_for_status()

            data = response.json()
            try:
                # OpenRouter can embed API-level errors inside a 200 response
                if "error" in data:
                    err = data["error"]
                    raise ValueError(
                        f"OpenRouter API error {err.get('code', '')}: {err.get('message', err)}"
                    )
                content = data["choices"][0]["message"].get("content")
                if content is None:
                    # Reasoning models (e.g. ring-2.6) may return content=null
                    # if max_tokens was exhausted during the thinking phase.
                    # Try extracting text from the reasoning field as a last resort.
                    reasoning = data["choices"][0]["message"].get("reasoning")
                    finish_reason = data["choices"][0].get("finish_reason", "")
                    if reasoning and finish_reason == "length":
                        logger.warning(
                            "Model returned null content (finish_reason=length). "
                            "Reasoning model likely hit max_tokens mid-think. "
                            "Increase max_tokens. Attempting to use partial reasoning text."
                        )
                        content = reasoning
                    else:
                        raise ValueError(
                            f"OpenRouter returned null content (model may be unavailable). "
                            f"Response: {data}"
                        )
                return content.strip()
            except (KeyError, IndexError) as exc:
                raise ValueError(f"Unexpected OpenRouter response shape: {data}") from exc

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in (429, 402):
                raise
            last_exc = exc

    raise last_exc  # all retries exhausted


async def openrouter_generate_image(
    prompt: str,
    *,
    model: str | None = None,
    n: int = 1,
    api_key: str | None = None,
) -> str:
    """
    Generate an image from a text prompt.

    Strategy (tried in order):
      1. ModelsLab API  — used when IMAGEGEN_API_KEY is set in .env or passed in request
      2. OpenRouter images/generations — fallback using the existing OPENROUTER_API_KEY

    Retries up to _MAX_RETRIES times on 429 with exponential backoff.

    Returns:
        A URL string or a data URI (data:image/png;base64,...).

    Raises:
        httpx.HTTPStatusError: on persistent non-2xx errors.
        ValueError: if the response contains no image data.
    """
    settings = get_settings()
    resolved_key = api_key or settings.IMAGEGEN_API_KEY

    if resolved_key:
        return await _modelslab_generate(prompt, resolved_key, model or settings.IMAGEGEN_MODEL, n)
    else:
        logger.info("IMAGEGEN_API_KEY not set — falling back to OpenRouter image generation")
        return await _openrouter_image_generate(prompt, model or settings.IMAGEGEN_MODEL, n)


async def _modelslab_generate(prompt: str, api_key: str, model_id: str, n: int) -> str:
    """Call ModelsLab text2img API and return a base64 data URI."""
    headers = {"Content-Type": "application/json"}
    payload = {"key": api_key, "prompt": prompt, "model_id": model_id, "samples": n}

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://modelslab.com/api/v6/images/text2img",
                    headers=headers,
                    json=payload,
                )

            if response.status_code == 429:
                wait = 2 ** attempt
                logger.warning("ModelsLab 429 attempt %d/%d — waiting %ds", attempt + 1, _MAX_RETRIES, wait)
                await asyncio.sleep(wait)
                last_exc = httpx.HTTPStatusError("429", request=response.request, response=response)
                continue

            response.raise_for_status()
            data = response.json()

            image_url = None
            if "output" in data and isinstance(data["output"], list) and data["output"]:
                image_url = data["output"][0]
            elif "image_url" in data:
                image_url = data["image_url"]
            elif "url" in data:
                image_url = data["url"]

            if not image_url:
                raise ValueError(f"No image URL in ModelsLab response: {data}")

            if isinstance(image_url, str) and image_url.startswith("http"):
                async with httpx.AsyncClient(timeout=30.0) as img_client:
                    img_resp = await img_client.get(image_url)
                    img_resp.raise_for_status()
                    b64 = base64.b64encode(img_resp.content).decode("utf-8")
                    return f"data:image/png;base64,{b64}"
            if isinstance(image_url, str) and image_url.startswith("data:"):
                return image_url
            raise ValueError(f"Unexpected image_url format: {image_url}")

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 429:
                raise
            last_exc = exc

    raise last_exc


async def _openrouter_image_generate(prompt: str, model: str, n: int) -> str:
    """Fall back to OpenRouter images/generations endpoint."""
    settings = get_settings()
    headers = _build_headers(settings)
    payload = {"model": model, "prompt": prompt, "n": n}

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{_OPENROUTER_BASE}/images/generations",
                    headers=headers,
                    json=payload,
                )

            if response.status_code in (429, 402):
                wait = 2 ** attempt
                logger.warning("OpenRouter image %d attempt %d/%d — waiting %ds",
                               response.status_code, attempt + 1, _MAX_RETRIES, wait)
                await asyncio.sleep(wait)
                last_exc = httpx.HTTPStatusError(str(response.status_code), request=response.request, response=response)
                continue

            response.raise_for_status()
            data = response.json()

            image_data = data["data"][0]
            url = image_data.get("url")
            b64 = image_data.get("b64_json")
            if url:
                return url
            if b64:
                return f"data:image/png;base64,{b64}"
            raise ValueError(f"No image data in OpenRouter response: {data}")

        except (KeyError, IndexError) as exc:
            raise ValueError(f"Unexpected OpenRouter image response: {data}") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in (429, 402):
                raise
            last_exc = exc

    raise last_exc
