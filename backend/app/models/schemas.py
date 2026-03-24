from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ── Ingestion Models ──────────────────────────────────────────────

class Section(BaseModel):
    """A detected section from the paper."""
    title: str
    text: str
    page_numbers: list[int] = []


class Chunk(BaseModel):
    """A semantic chunk with metadata."""
    chunk_id: int
    text: str
    section_title: str = ""
    page_number: int = 0
    paper_id: str = ""


class PaperMetadata(BaseModel):
    """Extracted metadata from a paper."""
    paper_id: str
    title: str = "Untitled"
    authors: list[str] = []
    abstract: str = ""
    sections: list[str] = []
    total_pages: int = 0
    filename: str = ""


# ── API Request / Response Models ─────────────────────────────────

class UploadResponse(BaseModel):
    paper_id: str
    metadata: PaperMetadata
    num_chunks: int
    message: str = "Paper uploaded and processed successfully"


class QueryRequest(BaseModel):
    paper_id: str
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class SourceChunk(BaseModel):
    """A retrieved source chunk with relevance info."""
    text: str
    section_title: str
    page_number: int
    similarity_score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = []
    grounded: bool = True  # False if answer could not be found


class SummaryLevel(str, Enum):
    BEGINNER = "beginner"
    TECHNICAL = "technical"


class SummaryResponse(BaseModel):
    paper_id: str
    level: SummaryLevel
    summary: str
    sections: list[Section] = []


# ── Multi-Document Models ────────────────────────────────────────

class CompareRequest(BaseModel):
    paper_ids: list[str] = Field(..., min_length=2)
    question: str = "Compare these papers"


class CompareResponse(BaseModel):
    answer: str
    sources: dict[str, list[SourceChunk]] = {}


class SimilarityResponse(BaseModel):
    paper_id_a: str
    paper_id_b: str
    similarity_score: float
    common_topics: list[str] = []
