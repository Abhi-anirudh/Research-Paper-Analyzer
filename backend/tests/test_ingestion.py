"""Tests for the ingestion pipeline."""

import os
import pytest
from unittest.mock import patch, MagicMock
from app.models.schemas import Section, Chunk
from app.ingestion.chunker import chunk_section, chunk_document, _split_into_paragraphs, _merge_small_paragraphs
from app.ingestion.metadata import extract_metadata, _extract_title, _extract_abstract


# ── Chunker Tests ──────────────────────────────────────────────────

class TestSplitIntoParagraphs:
    def test_splits_on_double_newline(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        result = _split_into_paragraphs(text)
        assert len(result) == 3
        assert result[0] == "First paragraph."
        assert result[1] == "Second paragraph."

    def test_handles_single_paragraph(self):
        text = "Just one paragraph with no breaks."
        result = _split_into_paragraphs(text)
        assert len(result) == 1

    def test_filters_empty_strings(self):
        text = "First.\n\n\n\n\nSecond."
        result = _split_into_paragraphs(text)
        assert all(p.strip() for p in result)


class TestMergeSmallParagraphs:
    def test_merges_small_chunks(self):
        paragraphs = ["Hi.", "Hello.", "World."]
        result = _merge_small_paragraphs(paragraphs)
        # All are tiny, should merge
        assert len(result) <= 2

    def test_preserves_large_paragraphs(self):
        large = "x " * 500  # Large paragraph
        paragraphs = [large, "small"]
        result = _merge_small_paragraphs(paragraphs)
        assert len(result) >= 1


class TestChunkSection:
    def test_produces_chunks(self):
        section = Section(
            title="Introduction",
            text="This is a test paragraph.\n\nAnother paragraph with more content here.",
            page_numbers=[1, 2],
        )
        chunks = chunk_section(section, "test-paper", start_id=0)
        assert len(chunks) >= 1
        assert all(isinstance(c, Chunk) for c in chunks)
        assert chunks[0].section_title == "Introduction"
        assert chunks[0].paper_id == "test-paper"

    def test_empty_section_returns_empty(self):
        section = Section(title="Empty", text="", page_numbers=[])
        chunks = chunk_section(section, "test")
        assert len(chunks) == 0


class TestChunkDocument:
    def test_chunks_multiple_sections(self):
        sections = [
            Section(title="Abstract", text="This is the abstract of the paper.", page_numbers=[1]),
            Section(title="Methods", text="We used method X and method Y.", page_numbers=[2]),
        ]
        chunks = chunk_document(sections, "paper-1")
        assert len(chunks) >= 2
        assert chunks[0].chunk_id == 0
        # IDs should be sequential
        ids = [c.chunk_id for c in chunks]
        assert ids == list(range(len(chunks)))


# ── Metadata Tests ─────────────────────────────────────────────────

class TestExtractMetadata:
    def test_basic_metadata(self):
        sections = [
            Section(title="Preamble", text="My Great Paper Title\nJohn Doe, Jane Smith\nUniversity of Test", page_numbers=[1]),
            Section(title="Abstract", text="This paper presents a novel approach.", page_numbers=[1]),
            Section(title="Introduction", text="In recent years...", page_numbers=[2]),
        ]
        meta = extract_metadata(sections, "p1", "paper.pdf", 10)
        assert meta.paper_id == "p1"
        assert meta.filename == "paper.pdf"
        assert meta.total_pages == 10
        assert "Abstract" in meta.sections

    def test_extracts_abstract(self):
        sections = [
            Section(title="Abstract", text="We propose a new framework.", page_numbers=[1]),
        ]
        abstract = _extract_abstract(sections)
        assert "framework" in abstract

    def test_title_from_preamble(self):
        sections = [
            Section(title="Preamble", text="Attention Is All You Need\nAuthors here", page_numbers=[1]),
        ]
        title = _extract_title(sections)
        assert title == "Attention Is All You Need"
