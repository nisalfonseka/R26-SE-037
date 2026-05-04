"""
Sinhala text preprocessing — cleaning and normalization.

Handles:
  - Unicode normalization (NFC)
  - Removal of HTML tags and URLs
  - Whitespace normalization
  - Removal of invisible/control characters
  - Standardization of Sinhala punctuation
"""

import re
import unicodedata


# ── Regex patterns (compiled once) ──
_RE_HTML_TAG = re.compile(r"<[^>]+>")
_RE_URL = re.compile(
    r"https?://[^\s<>\"']+|www\.[^\s<>\"']+"
)
_RE_MULTI_SPACE = re.compile(r"[ \t]+")
_RE_MULTI_NEWLINE = re.compile(r"\n{3,}")
_RE_CONTROL_CHARS = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]"
)


def clean_text(text: str) -> str:
    """
    Clean and normalize raw Sinhala text.

    Steps:
      1. Unicode NFC normalization
      2. Strip HTML tags
      3. Strip URLs
      4. Remove invisible/control characters
      5. Normalize whitespace (collapse multiple spaces/tabs → single space)
      6. Collapse excessive newlines (3+ → 2)
      7. Strip leading/trailing whitespace

    Args:
        text: Raw input text, potentially containing noise.

    Returns:
        Cleaned and normalized text.
    """
    if not text:
        return ""

    # 1. Unicode NFC normalization — canonical composition
    text = unicodedata.normalize("NFC", text)

    # 2. Remove HTML tags
    text = _RE_HTML_TAG.sub("", text)

    # 3. Remove URLs
    text = _RE_URL.sub("", text)

    # 4. Remove control characters (keep newlines, tabs initially)
    text = _RE_CONTROL_CHARS.sub("", text)

    # 5. Normalize whitespace within lines
    text = _RE_MULTI_SPACE.sub(" ", text)

    # 6. Collapse excessive newlines
    text = _RE_MULTI_NEWLINE.sub("\n\n", text)

    # 7. Strip leading/trailing whitespace per line and overall
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines).strip()

    return text
