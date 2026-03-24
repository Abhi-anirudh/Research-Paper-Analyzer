"""Query router — handles question-answering and advanced queries."""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    QueryRequest, QueryResponse,
    CompareRequest, CompareResponse,
)
from app.generation.generator import (
    answer_question,
    detect_novelty,
    extract_key_insights,
    compare_papers,
    generate_literature_review,
)

router = APIRouter(tags=["Query"])


@router.post("/query", response_model=QueryResponse)
async def query_paper(request: QueryRequest):
    """Ask a question about an uploaded paper.

    The RAG pipeline retrieves relevant chunks and generates an
    answer grounded strictly in the paper content.
    """
    try:
        answer, sources, is_grounded = answer_question(
            paper_id=request.paper_id,
            question=request.question,
            top_k=request.top_k,
        )
        return QueryResponse(answer=answer, sources=sources, grounded=is_grounded)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Paper '{request.paper_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/novelty", response_model=QueryResponse)
async def novelty_detection(request: QueryRequest):
    """Detect what makes this paper novel and different."""
    try:
        answer, sources = detect_novelty(request.paper_id)
        return QueryResponse(answer=answer, sources=sources, grounded=True)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Paper '{request.paper_id}' not found")


@router.post("/query/insights", response_model=QueryResponse)
async def key_insights(request: QueryRequest):
    """Extract key insights from the paper."""
    try:
        answer, sources = extract_key_insights(request.paper_id)
        return QueryResponse(answer=answer, sources=sources, grounded=True)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Paper '{request.paper_id}' not found")


@router.post("/compare", response_model=CompareResponse)
async def compare(request: CompareRequest):
    """Compare multiple papers."""
    try:
        answer, all_sources = compare_papers(request.paper_ids, request.question)
        return CompareResponse(answer=answer, sources=all_sources)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/literature-review", response_model=CompareResponse)
async def literature_review(request: CompareRequest):
    """Generate a literature review across multiple papers."""
    try:
        answer, all_sources = generate_literature_review(request.paper_ids)
        return CompareResponse(answer=answer, sources=all_sources)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
