"""
Named Entity Recognition (NER) for Sinhala text.

Uses rule-based pattern matching for common Sinhala entity types.
Will be replaced with a fine-tuned NER model (SinLlama) in production.

Supported entity types:
  - PERSON   : Personal names (detected by common Sinhala name suffixes)
  - ORG      : Organization names (detected by org keywords)
  - LOC      : Locations / geographic names
  - DATE     : Date expressions
  - NUMBER   : Numeric amounts / quantities
  - EVENT    : Named events
"""

import re

from app.schemas.headline import EntityInfo


# ── Sinhala entity patterns ──

# Organization keywords commonly found in Sinhala news
_ORG_KEYWORDS = [
    "සංවිධානය", "සමිතිය", "සමාගම", "කමිටුව", "මණ්ඩලය",
    "බැංකුව", "විශ්වවිද්‍යාලය", "රෝහල", "පාර්ලිමේන්තුව",
    "අධිකරණය", "ආයතනය", "දෙපාර්තමේන්තුව", "අමාත්‍යාංශය",
    "පදනම", "සංස්ථාව", "සභාව", "ප්‍රාදේශීය සභාව",
    "මහ බැංකුව", "මැතිවරණ කොමිසම",
]

# Location keywords
_LOC_KEYWORDS = [
    "නගරය", "දිස්ත්‍රික්කය", "පළාත", "ගම", "මාවත",
    "වීදිය", "ප්‍රදේශය", "රට", "දූපත", "කඳුකරය",
    "කොළඹ", "ගාල්ල", "මාතර", "කුරුණෑගල", "මහනුවර",
    "යාපනය", "බදුල්ල", "රත්නපුර", "අනුරාධපුරය",
    "පොළොන්නරුව", "ත්‍රිකුණාමලය", "හම්බන්තොට",
    "ශ්‍රී ලංකාව", "ඉන්දියාව", "චීනය", "ජපානය",
]

# Person name suffixes common in formal Sinhala
_PERSON_SUFFIXES = [
    "මහතා", "මහත්මිය", "මහත්මීය", "මැතිතුමා", "මැතිණිය",
    "ජනාධිපති", "අගමැති", "ඇමති", "ලේකම්",
    "නිලධාරි", "පූජ්‍ය", "ආචාර්ය",
]

# Date-related patterns
_RE_SINHALA_DATE = re.compile(
    r"\d{4}[./\-]\d{1,2}[./\-]\d{1,2}"
    r"|\d{1,2}[./\-]\d{1,2}[./\-]\d{4}"
    r"|\d{4}\s*(?:ජනවාරි|පෙබරවාරි|මාර්තු|අප්‍රේල්|මැයි|ජූනි|ජූලි|අගෝස්තු|සැප්තැම්බර්|ඔක්තෝබර්|නොවැම්බර්|දෙසැම්බර්)"
)

# Number / quantity patterns
_RE_NUMBER = re.compile(
    r"(?:රු(?:පියල්)?\.?\s*\d[\d,]*(?:\.\d+)?)"  # currency
    r"|(?:\d[\d,]*(?:\.\d+)?%)"                     # percentages
    r"|(?:\d[\d,]*(?:\.\d+)?)",                     # plain numbers
)


def extract_entities(text: str) -> list[EntityInfo]:
    """
    Extract named entities from Sinhala text using rule-based patterns.

    This is a lightweight, dependency-free extractor designed as a placeholder
    until a fine-tuned NER model is integrated.

    Args:
        text: Cleaned Sinhala text.

    Returns:
        List of EntityInfo objects with entity text, type, and offsets.
    """
    entities: list[EntityInfo] = []
    seen_spans: set[tuple[int, int]] = set()

    def _add_entity(start: int, end: int, surface: str, label: str):
        span = (start, end)
        if span not in seen_spans:
            seen_spans.add(span)
            entities.append(EntityInfo(
                text=surface.strip(),
                label=label,
                start=start,
                end=end,
            ))

    # ── DATE entities ──
    for m in _RE_SINHALA_DATE.finditer(text):
        _add_entity(m.start(), m.end(), m.group(), "DATE")

    # ── NUMBER entities ──
    for m in _RE_NUMBER.finditer(text):
        _add_entity(m.start(), m.end(), m.group(), "NUMBER")

    # ── ORG entities ──
    for kw in _ORG_KEYWORDS:
        start = 0
        while True:
            pos = text.find(kw, start)
            if pos == -1:
                break
            # Expand left to capture the full org name (up to previous punctuation)
            org_start = _expand_left(text, pos)
            surface = text[org_start:pos + len(kw)]
            _add_entity(org_start, pos + len(kw), surface, "ORG")
            start = pos + len(kw)

    # ── LOC entities ──
    for kw in _LOC_KEYWORDS:
        start = 0
        while True:
            pos = text.find(kw, start)
            if pos == -1:
                break
            loc_start = _expand_left(text, pos)
            surface = text[loc_start:pos + len(kw)]
            _add_entity(loc_start, pos + len(kw), surface, "LOC")
            start = pos + len(kw)

    # ── PERSON entities ──
    for suffix in _PERSON_SUFFIXES:
        start = 0
        while True:
            pos = text.find(suffix, start)
            if pos == -1:
                break
            # Expand left to capture the name before the title
            person_start = _expand_left(text, pos)
            surface = text[person_start:pos + len(suffix)]
            _add_entity(person_start, pos + len(suffix), surface, "PERSON")
            start = pos + len(suffix)

    # Sort by position
    entities.sort(key=lambda e: e.start)

    return entities


def _expand_left(text: str, pos: int, max_chars: int = 60) -> int:
    """
    Expand left from a position to find the start of a name phrase.
    Stops at sentence boundaries, commas, or the max character limit.
    """
    boundary = max(0, pos - max_chars)
    search_region = text[boundary:pos]

    # Find the last sentence boundary or comma
    for delim in [".", ",", "!", "?", "।", "\n"]:
        last_delim = search_region.rfind(delim)
        if last_delim != -1:
            return boundary + last_delim + 1

    return boundary
