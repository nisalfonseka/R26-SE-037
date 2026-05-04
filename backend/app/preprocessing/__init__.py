"""
Preprocessing __init__ — expose public API of the preprocessing package.
"""

from app.preprocessing.cleaner import clean_text
from app.preprocessing.tokenizer import (
    split_sentences,
    tokenize_words,
    get_word_count,
)

__all__ = [
    "clean_text",
    "split_sentences",
    "tokenize_words",
    "get_word_count",
]
