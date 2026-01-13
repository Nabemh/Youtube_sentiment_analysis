"""Lightweight text cleaning utilities for sentiment analysis.

Functions:
- clean_text(text): lowercasing, URL removal, punctuation cleanup, strip extra spaces.

Intentionally *minimal* – keeps words intact (no stemming/lemmatization) to preserve meaning.
"""
from __future__ import annotations

import re
import string
from typing import List

# Precompile regex patterns
URL_REGEX = re.compile(r"https?://\S+|www\.\S+")
PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def clean_text(text: str) -> str:
    """Return lightly-cleaned version of *text* suitable for vectorization."""
    text = text.lower()
    text = URL_REGEX.sub("", text)
    # Remove punctuation but keep intra-word apostrophes (e.g. don't)
    text = text.translate(PUNCT_TABLE)
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    return text.strip()


def batch_clean(texts: List[str]) -> List[str]:
    """Clean a list of strings."""
    return [clean_text(t) for t in texts]
