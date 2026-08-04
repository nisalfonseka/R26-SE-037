"""
Headline validation service.

Checks generated headlines against quality thresholds:
  - Grammar correctness (reuses grammar checker rules)
  - Entity coverage (key entities from article present in headline)
  - Semantic alignment (character n-gram overlap as proxy)
  - Length constraints
  - ROUGE and BLEU-like metrics (simplified implementations)
"""

from collections import Counter

from app.preprocessing.tokenizer import tokenize_words
from app.schemas.headline import EntityInfo, ValidationMetrics
from app.services.grammar.grammar_rules import GRAMMAR_RULES


# ── Quality thresholds ──
THRESHOLD_ENTITY_COVERAGE = 0.3
THRESHOLD_ROUGE_1 = 0.15
THRESHOLD_SEMANTIC_SIM = 0.2


def validate_headline(
    headline: str,
    article_text: str,
    entities: list[EntityInfo],
    max_length: int = 80,
) -> ValidationMetrics:
    """
    Validate a headline against quality metrics.

    Returns a ValidationMetrics object with all scores computed.
    """
    h_tokens = tokenize_words(headline)
    a_tokens = tokenize_words(article_text)

    # ── ROUGE scores ──
    rouge_1 = _rouge_n(h_tokens, a_tokens, n=1)
    rouge_2 = _rouge_n(h_tokens, a_tokens, n=2)
    rouge_l = _rouge_l(h_tokens, a_tokens)

    # ── BLEU score ──
    bleu = _bleu(h_tokens, a_tokens)

    # ── Semantic similarity (char n-gram Jaccard as proxy) ──
    sem_sim = _char_ngram_similarity(headline, article_text, n=3)

    # ── Entity coverage ──
    ent_cov = _entity_coverage(headline, entities)

    # ── Grammar check ──
    grammar_pass = _grammar_check(headline)

    # ── Length check ──
    length_ok = len(headline) <= max_length and len(headline) >= 5

    return ValidationMetrics(
        rouge_1=round(rouge_1, 4),
        rouge_2=round(rouge_2, 4),
        rouge_l=round(rouge_l, 4),
        bleu=round(bleu, 4),
        semantic_similarity=round(sem_sim, 4),
        entity_coverage=round(ent_cov, 4),
        grammar_pass=grammar_pass,
        length_ok=length_ok,
    )


def passes_thresholds(metrics: ValidationMetrics) -> bool:
    """Check if all metrics pass the minimum quality thresholds."""
    return (
        metrics.rouge_1 >= THRESHOLD_ROUGE_1
        and metrics.semantic_similarity >= THRESHOLD_SEMANTIC_SIM
        and metrics.entity_coverage >= THRESHOLD_ENTITY_COVERAGE
        and metrics.grammar_pass
        and metrics.length_ok
    )


# ── Internal metric implementations ──

def _rouge_n(hypothesis: list[str], reference: list[str], n: int = 1) -> float:
    """Compute ROUGE-N F1 between hypothesis and reference token lists."""
    if not hypothesis or not reference:
        return 0.0

    h_ngrams = _get_ngrams(hypothesis, n)
    r_ngrams = _get_ngrams(reference, n)

    if not h_ngrams or not r_ngrams:
        return 0.0

    overlap = sum((h_ngrams & r_ngrams).values())
    precision = overlap / sum(h_ngrams.values()) if h_ngrams else 0
    recall = overlap / sum(r_ngrams.values()) if r_ngrams else 0

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def _get_ngrams(tokens: list[str], n: int) -> Counter:
    """Extract n-gram counts from token list."""
    ngrams = [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]
    return Counter(ngrams)


def _rouge_l(hypothesis: list[str], reference: list[str]) -> float:
    """Compute ROUGE-L F1 using longest common subsequence."""
    if not hypothesis or not reference:
        return 0.0

    lcs_len = _lcs_length(hypothesis, reference)
    precision = lcs_len / len(hypothesis) if hypothesis else 0
    recall = lcs_len / len(reference) if reference else 0

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def _lcs_length(x: list[str], y: list[str]) -> int:
    """Compute length of the longest common subsequence."""
    m, n = len(x), len(y)
    # Limit computation for very long texts
    if m > 200:
        x = x[:200]
        m = 200
    if n > 200:
        y = y[:200]
        n = 200

    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if x[i - 1] == y[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(curr[j - 1], prev[j])
        prev = curr
    return prev[n]


def _bleu(hypothesis: list[str], reference: list[str], max_n: int = 4) -> float:
    """Simplified BLEU score computation."""
    if not hypothesis or not reference:
        return 0.0

    scores = []
    for n in range(1, max_n + 1):
        h_ngrams = _get_ngrams(hypothesis, n)
        r_ngrams = _get_ngrams(reference, n)
        if not h_ngrams:
            scores.append(0.0)
            continue
        clipped = sum((h_ngrams & r_ngrams).values())
        total = sum(h_ngrams.values())
        scores.append(clipped / total if total > 0 else 0.0)

    # Geometric mean with brevity penalty
    import math
    if any(s == 0 for s in scores):
        return 0.0

    log_avg = sum(math.log(s) for s in scores) / len(scores)
    bp = min(1.0, math.exp(1 - len(reference) / len(hypothesis))) if hypothesis else 0
    return bp * math.exp(log_avg)


def _char_ngram_similarity(text1: str, text2: str, n: int = 3) -> float:
    """Character n-gram Jaccard similarity as a proxy for semantic similarity."""
    if not text1 or not text2:
        return 0.0

    ngrams1 = set(_char_ngrams(text1, n))
    ngrams2 = set(_char_ngrams(text2, n))

    if not ngrams1 or not ngrams2:
        return 0.0

    intersection = ngrams1 & ngrams2
    union = ngrams1 | ngrams2

    return len(intersection) / len(union)


def _char_ngrams(text: str, n: int) -> list[str]:
    """Extract character n-grams from text."""
    text = text.lower().replace(" ", "")
    return [text[i:i + n] for i in range(len(text) - n + 1)]


def _entity_coverage(headline: str, entities: list[EntityInfo]) -> float:
    """Fraction of source entities whose text appears in the headline."""
    if not entities:
        return 1.0  # No entities to check → pass

    headline_lower = headline.lower()
    found = sum(1 for e in entities if e.text.lower() in headline_lower)
    return found / len(entities)


def _grammar_check(headline: str) -> bool:
    """Check if the headline contains any known grammar errors."""
    for rule in GRAMMAR_RULES:
        pattern = rule["pattern"]
        replacement = rule["replacement"]
        if pattern == replacement:
            continue
        if pattern in headline:
            return False
    return True
