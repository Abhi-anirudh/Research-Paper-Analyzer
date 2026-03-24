"""Semantic chunker — splits sections into meaningful chunks preserving context."""

import re
from app.models.schemas import Chunk, Section


# Target chunk size in characters (≈ 300-500 tokens)
MIN_CHUNK_CHARS = 200
MAX_CHUNK_CHARS = 2000
OVERLAP_CHARS = 100


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs on double newlines or sentence boundaries."""
    # First try splitting on double newlines
    paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # If we get one giant block, split on sentence boundaries
    result = []
    for para in paragraphs:
        if len(para) > MAX_CHUNK_CHARS:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            result.extend(sentences)
        else:
            result.append(para)

    return result


def _merge_small_paragraphs(paragraphs: list[str]) -> list[str]:
    """Merge consecutive small paragraphs to meet minimum chunk size."""
    merged = []
    buffer = ""

    for para in paragraphs:
        if buffer and len(buffer) + len(para) + 1 > MAX_CHUNK_CHARS:
            merged.append(buffer.strip())
            buffer = para
        elif len(buffer) + len(para) + 1 < MIN_CHUNK_CHARS:
            buffer = f"{buffer}\n{para}" if buffer else para
        else:
            if buffer:
                merged.append(buffer.strip())
            buffer = para

    if buffer:
        merged.append(buffer.strip())

    return merged


def chunk_section(section: Section, paper_id: str, start_id: int = 0) -> list[Chunk]:
    """Chunk a single section into semantically meaningful pieces."""
    if not section.text.strip():
        return []

    paragraphs = _split_into_paragraphs(section.text)
    merged = _merge_small_paragraphs(paragraphs)

    chunks = []
    for i, text in enumerate(merged):
        chunks.append(Chunk(
            chunk_id=start_id + i,
            text=text,
            section_title=section.title,
            page_number=section.page_numbers[0] if section.page_numbers else 0,
            paper_id=paper_id,
        ))

    return chunks


def chunk_document(sections: list[Section], paper_id: str) -> list[Chunk]:
    """Chunk all sections of a document."""
    all_chunks = []
    chunk_id = 0

    for section in sections:
        section_chunks = chunk_section(section, paper_id, start_id=chunk_id)
        all_chunks.extend(section_chunks)
        chunk_id += len(section_chunks)

    return all_chunks
