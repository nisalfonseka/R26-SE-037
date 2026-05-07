"""
Style conditioning module for headline generation.

Injects predefined stylistic parameters into the generation prompt
based on the selected headline style. Each style defines:
  - tone          : overall emotional/tonal direction
  - formality     : formal / informal / neutral
  - urgency       : level of urgency to convey
  - max_words     : soft word-count target
  - prefix_hint   : optional prefix patterns typical for the style
  - prompt_suffix : style-specific instruction appended to the LLM prompt
"""

from dataclasses import dataclass, field

from app.schemas.headline import HeadlineStyle


@dataclass(frozen=True)
class StyleConfig:
    """Immutable configuration for a single headline style."""
    name: str
    tone: str
    formality: str
    urgency: str
    max_words: int
    prefix_hint: str
    prompt_suffix: str
    # Additional style-specific Sinhala instructions for the LLM
    sinhala_instruction: str = ""


# ── Predefined style configurations ──

_STYLE_MAP: dict[HeadlineStyle, StyleConfig] = {
    HeadlineStyle.FORMAL: StyleConfig(
        name="Formal",
        tone="neutral, authoritative",
        formality="formal",
        urgency="low",
        max_words=12,
        prefix_hint="",
        prompt_suffix=(
            "Generate a formal, objective headline suitable for a broadsheet newspaper. "
            "Use concise, authoritative language. Avoid colloquialisms."
        ),
        sinhala_instruction=(
            "පුවත්පත් ශෛලියේ විධිමත් ශීර්ෂයක් ලියන්න. "
            "කෙටි, නිවැරදි, සහ නිල භාෂාව භාවිතා කරන්න."
        ),
    ),

    HeadlineStyle.BREAKING_NEWS: StyleConfig(
        name="Breaking News",
        tone="urgent, alarming",
        formality="semi-formal",
        urgency="high",
        max_words=10,
        prefix_hint="වේගයෙන්: ",
        prompt_suffix=(
            "Generate an urgent, attention-grabbing breaking news headline. "
            "Convey immediacy. Use active voice and present tense."
        ),
        sinhala_instruction=(
            "හදිසි ප්‍රවෘත්ති ශීර්ෂයක් ලියන්න. "
            "ක්ෂණික බව සහ වැදගත්කම ප්‍රකාශ කරන්න. "
            "වර්තමාන කාලය සහ ක්‍රියාකාරී හඬ භාවිතා කරන්න."
        ),
    ),

    HeadlineStyle.YOUTH: StyleConfig(
        name="Youth-oriented",
        tone="casual, engaging",
        formality="informal",
        urgency="medium",
        max_words=14,
        prefix_hint="",
        prompt_suffix=(
            "Generate a catchy, youth-oriented headline that uses contemporary language. "
            "Make it engaging and shareable on social media."
        ),
        sinhala_instruction=(
            "තරුණ පරපුර ආකර්ෂණය කර ගන්නා ශීර්ෂයක් ලියන්න. "
            "නවීන භාෂාව භාවිතා කරන්න. සමාජ මාධ්‍ය හිතකාමී විය යුතුය."
        ),
    ),

    HeadlineStyle.EDITORIAL: StyleConfig(
        name="Editorial",
        tone="analytical, thought-provoking",
        formality="formal",
        urgency="low",
        max_words=15,
        prefix_hint="",
        prompt_suffix=(
            "Generate an editorial-style headline that presents a perspective or analysis. "
            "Include a hint of opinion or commentary."
        ),
        sinhala_instruction=(
            "විශ්ලේෂණාත්මක, චින්තනය අවුස්සන සංස්කාදකීය ශීර්ෂයක් ලියන්න. "
            "මතයක් හෝ විචාරයක් ගම්‍ය වන සේ ලියන්න."
        ),
    ),
}


def get_style_config(style: HeadlineStyle) -> StyleConfig:
    """
    Retrieve the StyleConfig for the given headline style.

    Args:
        style: The HeadlineStyle enum value.

    Returns:
        A frozen StyleConfig dataclass with all style parameters.

    Raises:
        ValueError: If the style is not found in the style map.
    """
    config = _STYLE_MAP.get(style)
    if config is None:
        raise ValueError(f"Unknown headline style: {style}")
    return config


def build_style_prompt(
    style: HeadlineStyle,
    article_summary: str,
    entities_text: str,
) -> str:
    """
    Build the full LLM prompt with style conditioning injected.

    Args:
        style:           The desired headline style.
        article_summary: A condensed version of the source article.
        entities_text:   Comma-separated list of key entities.

    Returns:
        A formatted prompt string ready for the LLM.
    """
    config = get_style_config(style)

    prompt_parts = [
        f"[Style: {config.name}]",
        f"[Tone: {config.tone}]",
        f"[Formality: {config.formality}]",
        f"[Urgency: {config.urgency}]",
        f"[Max Words: {config.max_words}]",
        "",
        config.prompt_suffix,
        "",
        config.sinhala_instruction,
        "",
        f"Key entities: {entities_text}",
        "",
        "Article summary:",
        article_summary,
        "",
        "Generate a Sinhala headline:",
    ]

    return "\n".join(prompt_parts)
