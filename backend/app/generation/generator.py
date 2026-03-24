"""RAG generator — combines retrieval with LLM generation."""

from app.models.schemas import SourceChunk, SummaryLevel
from app.retrieval.retriever import retrieve, retrieve_multi
from app.generation.llm import generate
from app.config import get_settings
from app.generation.prompts import (
    SYSTEM_PROMPT,
    QUERY_TEMPLATE,
    BEGINNER_SUMMARY_TEMPLATE,
    TECHNICAL_SUMMARY_TEMPLATE,
    NOVELTY_DETECTION_TEMPLATE,
    KEY_INSIGHTS_TEMPLATE,
    COMPARISON_TEMPLATE,
    LITERATURE_REVIEW_TEMPLATE,
)


def _format_context(sources: list[SourceChunk]) -> str:
    """Format source chunks into a context string for the LLM."""
    parts = []
    for i, s in enumerate(sources, 1):
        parts.append(
            f"[Excerpt {i} | Section: {s.section_title} | Page: {s.page_number}]\n{s.text}"
        )
    return "\n\n".join(parts)


def answer_question(
    paper_id: str,
    question: str,
    top_k: int = 5,
) -> tuple[str, list[SourceChunk], bool]:
    """Answer a question using RAG.

    Returns:
        Tuple of (answer_text, source_chunks, is_grounded).
    """
    sources, is_grounded = retrieve(paper_id, question, top_k)

    if not is_grounded or not sources:
        return (
            "This information is not found in the paper. The retrieved context "
            "does not contain enough relevant information to answer this question.",
            sources,
            False,
        )

    context = _format_context(sources)
    user_prompt = QUERY_TEMPLATE.format(context=context, question=question)
    answer = generate(SYSTEM_PROMPT, user_prompt)

    return answer, sources, True


def generate_summary(
    paper_id: str,
    level: SummaryLevel,
    top_k: int = 15,
) -> tuple[str, list[SourceChunk]]:
    """Generate a paper summary at the specified level.

    Uses a broad retrieval (high top_k) to capture the full paper.
    """
    # Use multiple queries to get broad coverage
    queries = [
        "What is the main contribution and methodology?",
        "What are the key results and findings?",
        "What is the background and motivation?",
        "What are the limitations and conclusions?",
    ]

    all_sources: list[SourceChunk] = []
    seen_texts: set[str] = set()

    for q in queries:
        sources, _ = retrieve(paper_id, q, top_k=top_k)
        for s in sources:
            if s.text not in seen_texts:
                all_sources.append(s)
                seen_texts.add(s.text)

    context = _format_context(all_sources)
    template = (
        BEGINNER_SUMMARY_TEMPLATE if level == SummaryLevel.BEGINNER
        else TECHNICAL_SUMMARY_TEMPLATE
    )
    user_prompt = template.format(context=context)
    settings = get_settings()
    summary = generate(SYSTEM_PROMPT, user_prompt, model_name=settings.summary_model)

    return summary, all_sources


def detect_novelty(paper_id: str) -> tuple[str, list[SourceChunk]]:
    """Detect what makes this paper novel."""
    sources, _ = retrieve(paper_id, "What is novel and different about this approach?", top_k=10)
    context = _format_context(sources)
    user_prompt = NOVELTY_DETECTION_TEMPLATE.format(context=context)
    settings = get_settings()
    answer = generate(SYSTEM_PROMPT, user_prompt, model_name=settings.advanced_model)
    return answer, sources


def extract_key_insights(paper_id: str) -> tuple[str, list[SourceChunk]]:
    """Extract key insights from the paper."""
    sources, _ = retrieve(paper_id, "What are the key findings and insights?", top_k=10)
    context = _format_context(sources)
    user_prompt = KEY_INSIGHTS_TEMPLATE.format(context=context)
    settings = get_settings()
    answer = generate(SYSTEM_PROMPT, user_prompt, model_name=settings.advanced_model)
    return answer, sources


def compare_papers(
    paper_ids: list[str],
    question: str = "Compare these papers",
) -> tuple[str, dict[str, list[SourceChunk]]]:
    """Compare multiple papers."""
    all_sources = retrieve_multi(paper_ids, question, top_k=5)

    papers_context_parts = []
    for pid, sources in all_sources.items():
        context = _format_context(sources)
        papers_context_parts.append(f"--- PAPER: {pid} ---\n{context}")

    papers_context = "\n\n".join(papers_context_parts)
    user_prompt = COMPARISON_TEMPLATE.format(papers_context=papers_context, question=question)
    settings = get_settings()
    answer = generate(SYSTEM_PROMPT, user_prompt, model_name=settings.advanced_model)

    return answer, all_sources


def generate_literature_review(paper_ids: list[str]) -> tuple[str, dict[str, list[SourceChunk]]]:
    """Generate a literature review across multiple papers."""
    all_sources = retrieve_multi(paper_ids, "main contribution methodology results", top_k=8)

    papers_context_parts = []
    for pid, sources in all_sources.items():
        context = _format_context(sources)
        papers_context_parts.append(f"--- PAPER: {pid} ---\n{context}")

    papers_context = "\n\n".join(papers_context_parts)
    user_prompt = LITERATURE_REVIEW_TEMPLATE.format(papers_context=papers_context)
    settings = get_settings()
    answer = generate(SYSTEM_PROMPT, user_prompt, model_name=settings.advanced_model)

    return answer, all_sources
