"""Retriever — finds top-k relevant chunks with anti-hallucination gating."""

from app.config import get_settings
from app.models.schemas import Chunk, SourceChunk
from app.retrieval.embeddings import embed_query
from app.retrieval.vector_store import VectorStore


def retrieve(
    paper_id: str,
    question: str,
    top_k: int | None = None,
) -> tuple[list[SourceChunk], bool]:
    """Retrieve the most relevant chunks for a question.

    Args:
        paper_id: The paper to search in.
        question: The user's question.
        top_k: Number of chunks to retrieve (default from config).

    Returns:
        Tuple of (source_chunks, is_grounded).
        is_grounded is False if max similarity is below the threshold.
    """
    settings = get_settings()
    k = top_k or settings.top_k

    query_emb = embed_query(question)
    store = VectorStore(paper_id)
    results = store.search(query_emb, top_k=k)

    if not results:
        return [], False

    # Anti-hallucination gate
    max_score = max(score for _, score in results)
    is_grounded = max_score >= settings.similarity_threshold

    source_chunks = [
        SourceChunk(
            text=chunk.text,
            section_title=chunk.section_title,
            page_number=chunk.page_number,
            similarity_score=round(score, 4),
        )
        for chunk, score in results
    ]

    return source_chunks, is_grounded


def retrieve_multi(
    paper_ids: list[str],
    question: str,
    top_k: int = 3,
) -> dict[str, list[SourceChunk]]:
    """Retrieve chunks across multiple papers for comparison queries."""
    all_sources: dict[str, list[SourceChunk]] = {}

    for pid in paper_ids:
        sources, _ = retrieve(pid, question, top_k=top_k)
        all_sources[pid] = sources

    return all_sources
