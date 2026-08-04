"""
Sinhala text tokenizer — sentence splitting and word tokenization.

Provides lightweight tokenization for Sinhala text without heavy NLP
dependencies. Uses Unicode-aware regex patterns tuned for the Sinhala
script (U+0D80 – U+0DFF).
"""

import re


# ── Sinhala Unicode range ──
_SINHALA_RANGE = r"\u0D80-\u0DFF"

# ── Sentence boundary regex ──
# Splits on Sinhala full stops (।), standard period, question/exclamation marks
# followed by whitespace or end-of-string.
_RE_SENTENCE_BOUNDARY = re.compile(
    r"(?<=[.!?।])\s+(?=[A-Z\u0D80-\u0DFF])|(?<=[.!?।])\s*$",
    re.UNICODE,
)

# ── Word tokenizer ──
# Matches sequences of Sinhala characters (including combining marks),
# or sequences of Latin alphanumerics, or single punctuation characters.
_RE_WORD_TOKEN = re.compile(
    rf"[{_SINHALA_RANGE}\u200D]+|[A-Za-z0-9]+|[^\s]",
    re.UNICODE,
)


def split_sentences(text: str) -> list[str]:
    """
    Split Sinhala text into sentences.

    Uses a combination of standard punctuation and Sinhala-specific
    sentence boundary markers.

    Args:
        text: Cleaned Sinhala text.

    Returns:
        List of sentence strings.
    """
    if not text:
        return []

    # Split on sentence boundaries
    raw_sentences = _RE_SENTENCE_BOUNDARY.split(text)

    # Filter empty strings and strip whitespace
    sentences = [s.strip() for s in raw_sentences if s and s.strip()]

    return sentences


def tokenize_words(text: str) -> list[str]:
    """
    Tokenize Sinhala text into individual word tokens.

    Handles Sinhala script, Latin characters, numbers, and punctuation.

    Args:
        text: Cleaned Sinhala text (sentence or paragraph).

    Returns:
        List of token strings.
    """
    if not text:
        return []

    return _RE_WORD_TOKEN.findall(text)


def get_word_count(text: str) -> int:
    """Return the number of word tokens in the text."""
    # Exclude single punctuation tokens from the count
    tokens = tokenize_words(text)
    return sum(1 for t in tokens if len(t) > 1 or t.isalnum() or _is_sinhala_char(t))


def _is_sinhala_char(char: str) -> bool:
    """Check if a single character is in the Sinhala Unicode block."""
    if len(char) != 1:
        return False
    cp = ord(char)
    return 0x0D80 <= cp <= 0x0DFF
