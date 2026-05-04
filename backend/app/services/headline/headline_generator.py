"""
Core headline generator — produces headline candidates.

Uses rule-based extractive methods as a placeholder.
Will be replaced with a fine-tuned LLM (SinLlama) for controlled decoding.
"""

import re
from collections import Counter

from app.preprocessing.tokenizer import tokenize_words, split_sentences
from app.schemas.headline import HeadlineStyle, EntityInfo
from app.services.headline.style_conditioner import get_style_config


def generate_candidates(
    cleaned_text: str,
    entities: list[EntityInfo],
    style: HeadlineStyle,
    max_length: int = 80,
    num_candidates: int = 3,
) -> list[str]:
    """Generate headline candidates from cleaned article text."""
    style_config = get_style_config(style)
    sentences = split_sentences(cleaned_text)

    if not sentences:
        return [_fallback(cleaned_text, max_length, style_config.prefix_hint)]

    scored = _score_sentences(sentences, entities)
    top = sorted(scored, key=lambda x: x[1], reverse=True)

    candidates: list[str] = []
    for sentence, _ in top:
        if len(candidates) >= num_candidates:
            break
        h = _compress(sentence, entities, max_length, style_config)
        if h and h not in candidates:
            candidates.append(h)

    # Fill with variations
    if len(candidates) < num_candidates and candidates:
        for v in _variations(candidates[0], entities, num_candidates - len(candidates)):
            if v not in candidates:
                candidates.append(v)

    if not candidates:
        candidates.append(_fallback(cleaned_text, max_length, style_config.prefix_hint))

    return candidates[:num_candidates]


def _score_sentences(sentences, entities):
    all_tokens = []
    for s in sentences:
        all_tokens.extend(tokenize_words(s))
    tf = Counter(all_tokens)
    max_freq = max(tf.values()) if tf else 1
    entity_texts = {e.text.lower() for e in entities}

    scored = []
    for idx, sentence in enumerate(sentences):
        tokens = tokenize_words(sentence)
        if not tokens:
            scored.append((sentence, 0.0))
            continue
        tf_score = sum(tf[t] / max_freq for t in tokens) / len(tokens)
        pos_score = max(0, 1.0 - idx * 0.15)
        ent_score = sum(0.3 for et in entity_texts if et in sentence.lower())
        char_len = len(sentence)
        length_pen = 0.5 if char_len < 20 else (0.7 if char_len > 300 else 1.0)
        total = (tf_score * 0.3 + pos_score * 0.35 + ent_score * 0.35) * length_pen
        scored.append((sentence, total))
    return scored


def _compress(sentence, entities, max_length, style_config):
    h = sentence.strip()
    h = re.sub(r"\([^)]*\)", "", h)
    h = re.sub(r"\[[^\]]*\]", "", h)
    for fp in [r"එහෙත්\s*", r"කෙසේ වෙතත්\s*", r"මේ අතර\s*", r"ඒ අනුව\s*", r"එමෙන්ම\s*"]:
        h = re.sub(fp, "", h)
    h = re.sub(r"\s+", " ", h).strip()
    h = re.sub(r"\s+(?:සහ|හා|හෝ|නමුත්|එහෙත්)\s*$", "", h)
    if style_config.prefix_hint and not h.startswith(style_config.prefix_hint):
        h = style_config.prefix_hint + h
    if len(h) > max_length:
        h = _trunc(h, max_length)
    return h.rstrip(",;: ")


def _trunc(text, max_len):
    if len(text) <= max_len:
        return text
    t = text[:max_len]
    sp = t.rfind(" ")
    return t[:sp] if sp > max_len * 0.5 else t


def _variations(base, entities, count):
    vs = []
    if entities and count > 0:
        first = entities[0].text.strip()
        if not base.startswith(first):
            vs.append(_trunc(f"{first}: {base}", len(base) + 20))
    if count > len(vs):
        short = _trunc(base, int(len(base) * 0.7))
        if short != base:
            vs.append(short)
    return vs[:count]


def _fallback(text, max_length, prefix):
    h = text.strip()
    if prefix:
        h = prefix + h
    return _trunc(h, max_length)
