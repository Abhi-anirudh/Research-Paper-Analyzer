"""Embedding wrapper using sentence-transformers."""

import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache
from app.config import get_settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model (cached singleton)."""
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Encode a list of texts into normalized embeddings.

    Returns:
        np.ndarray of shape (len(texts), embedding_dim), L2-normalized.
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return np.array(embeddings, dtype=np.float32)


def embed_query(query: str) -> np.ndarray:
    """Encode a single query string."""
    return embed_texts([query])[0]
