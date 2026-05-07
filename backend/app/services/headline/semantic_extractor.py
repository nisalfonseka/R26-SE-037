"""
Semantic extraction module.

Extracts key themes, entities, and generates a visual prompt
from the final headline for downstream tasks like image generation.
"""

import re
from collections import Counter

from app.preprocessing.tokenizer import tokenize_words
from app.schemas.headline import EntityInfo, SemanticExtraction
from app.services.headline.entity_extractor import extract_entities


# Common Sinhala stop words to exclude from theme extraction
_STOP_WORDS = {
    "සහ", "හා", "හෝ", "ද", "ත්", "ට", "ගේ", "න්",
    "එය", "ඔහු", "ඇය", "ඔවුන්", "මේ", "ඒ", "මෙම",
    "ඇත", "ඇති", "නැත", "වේ", "විය", "කළ", "කරන",
    "බව", "ලෙස", "සේ", "පිළිබඳ", "සඳහා", "අතර",
    "මත", "හරහා", "තුළ", "පසු", "පෙර", "ඉහළ", "පහළ",
    "ලබා", "දී", "වන", "වූ", "යයි", "දැන්", "අද",
}


def extract_semantics(
    headline: str,
    article_text: str,
) -> SemanticExtraction:
    """
    Extract semantic information from the headline.

    Args:
        headline:     The final selected headline.
        article_text: The source article text (for context).

    Returns:
        SemanticExtraction with themes, entities, and visual prompt.
    """
    # Extract entities from the headline
    headline_entities = extract_entities(headline)

    # Extract key themes
    themes = _extract_themes(headline, article_text)

    # Generate a visual prompt
    visual_prompt = _generate_visual_prompt(headline, headline_entities, themes)

    return SemanticExtraction(
        key_themes=themes,
        entities=headline_entities,
        visual_prompt=visual_prompt,
    )


def _extract_themes(headline: str, article_text: str) -> list[str]:
    """Extract key themes by finding significant content words."""
    h_tokens = tokenize_words(headline)
    a_tokens = tokenize_words(article_text)

    # Filter stop words and short tokens
    content_tokens = [
        t for t in h_tokens
        if t not in _STOP_WORDS and len(t) > 2
    ]

    # Score by frequency in article (words in both headline and article are key)
    a_counter = Counter(a_tokens)
    scored = [(t, a_counter.get(t, 0)) for t in content_tokens]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Deduplicate and take top 5
    seen = set()
    themes = []
    for word, _ in scored:
        if word not in seen:
            seen.add(word)
            themes.append(word)
        if len(themes) >= 5:
            break

    return themes


def _generate_visual_prompt(
    headline: str,
    entities: list[EntityInfo],
    themes: list[str],
) -> str:
    """
    Generate a visual description prompt for image generation.

    Combines headline text, entity types, and themes into a
    descriptive prompt suitable for text-to-image models.
    """
    parts = []

    # Describe the scene based on entity types
    entity_types = {e.label for e in entities}
    if "PERSON" in entity_types:
        parts.append("A news scene featuring people")
    if "LOC" in entity_types:
        loc_names = [e.text for e in entities if e.label == "LOC"]
        parts.append(f"set in {', '.join(loc_names[:2])}")
    if "ORG" in entity_types:
        parts.append("involving institutional setting")
    if "EVENT" in entity_types:
        parts.append("depicting a significant event")

    # Add themes
    if themes:
        parts.append(f"related to {', '.join(themes[:3])}")

    # Add overall framing
    parts.append("| news photography style, editorial quality, high resolution")

    if not parts:
        return f"News illustration for: {headline}"

    return " ".join(parts)
