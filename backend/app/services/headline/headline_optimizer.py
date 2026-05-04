"""
Headline optimizer — enforces constraints on generated headlines.

Post-processes raw headline candidates to ensure:
  - Length within specified limits
  - Proper Sinhala punctuation and formatting
  - Removal of redundant words / repeated phrases
  - Readability improvements (no dangling particles)
"""

import re

from app.schemas.headline import HeadlineStyle
from app.services.headline.style_conditioner import get_style_config


def optimize_headline(
    headline: str,
    style: HeadlineStyle,
    max_length: int = 80,
) -> str:
    """
    Optimize a raw headline by applying constraint enforcement.

    Args:
        headline:   Raw generated headline text.
        style:      The target headline style.
        max_length: Maximum character length.

    Returns:
        Optimized headline string.
    """
    h = headline.strip()

    # 1. Remove duplicate consecutive words
    h = _remove_consecutive_duplicates(h)

    # 2. Normalize whitespace and punctuation
    h = re.sub(r"\s+", " ", h)
    h = re.sub(r"\s+([.!?,;:])", r"\1", h)

    # 3. Remove trailing incomplete particles
    trailing_particles = [
        "සහ", "හා", "හෝ", "නමුත්", "එහෙත්", "ද", "ත්",
        "ගේ", "ට", "න්", "ක්", "ය",
    ]
    for p in trailing_particles:
        if h.endswith(f" {p}"):
            h = h[: -(len(p) + 1)]

    # 4. Ensure proper ending
    if not h.endswith((".", "!", "?", "।")):
        # Headlines typically don't need periods, but remove trailing commas
        h = h.rstrip(",;:")

    # 5. Capitalize/format based on style
    style_config = get_style_config(style)
    if style_config.prefix_hint:
        if not h.startswith(style_config.prefix_hint):
            h = style_config.prefix_hint + h
        # Don't double the prefix
        double_prefix = style_config.prefix_hint + style_config.prefix_hint
        if h.startswith(double_prefix):
            h = h[len(style_config.prefix_hint):]

    # 6. Enforce max length at word boundary
    if len(h) > max_length:
        truncated = h[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.5:
            h = truncated[:last_space]
        else:
            h = truncated

    return h.strip()


def _remove_consecutive_duplicates(text: str) -> str:
    """Remove consecutive duplicate words."""
    words = text.split()
    result = [words[0]] if words else []
    for w in words[1:]:
        if w != result[-1]:
            result.append(w)
    return " ".join(result)
