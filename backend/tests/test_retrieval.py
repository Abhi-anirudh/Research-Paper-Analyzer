"""Tests for the retrieval layer."""

import numpy as np
import pytest
import tempfile
import os
from unittest.mock import patch

from app.models.schemas import Chunk
from app.retrieval.vector_store import VectorStore


class TestVectorStore:
    """Tests for FAISS vector store operations."""

    def setup_method(self):
        """Create a temp directory for test indices."""
        self.temp_dir = tempfile.mkdtemp()
        self.patcher = patch('app.retrieval.vector_store.get_settings')
        self.mock_settings = self.patcher.start()
        self.mock_settings.return_value.index_dir = self.temp_dir

    def teardown_method(self):
        """Clean up."""
        self.patcher.stop()
        # Clean temp files
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def _make_chunks(self, n: int) -> list[Chunk]:
        return [
            Chunk(
                chunk_id=i,
                text=f"Test chunk number {i}",
                section_title="Test Section",
                page_number=1,
                paper_id="test",
            )
            for i in range(n)
        ]

    def _make_embeddings(self, n: int, dim: int = 384) -> np.ndarray:
        rng = np.random.RandomState(42)
        emb = rng.randn(n, dim).astype(np.float32)
        # L2 normalize
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        return emb / norms

    def test_build_and_search(self):
        chunks = self._make_chunks(5)
        embeddings = self._make_embeddings(5)

        store = VectorStore("test-paper")
        store.build(chunks, embeddings)

        # Search with first chunk's embedding
        results = store.search(embeddings[0], top_k=3)
        assert len(results) == 3
        assert results[0][0].chunk_id == 0  # Most similar to itself
        assert results[0][1] >= results[1][1]  # Scores descending

    def test_persistence(self):
        chunks = self._make_chunks(3)
        embeddings = self._make_embeddings(3)

        # Build and save
        store1 = VectorStore("persist-test")
        store1.build(chunks, embeddings)
        assert store1.exists()

        # Load in new instance
        store2 = VectorStore("persist-test")
        results = store2.search(embeddings[0], top_k=2)
        assert len(results) == 2
        assert results[0][0].text == chunks[0].text

    def test_nonexistent_paper(self):
        store = VectorStore("does-not-exist")
        assert not store.exists()
        with pytest.raises(FileNotFoundError):
            store.search(np.zeros(384, dtype=np.float32))

    def test_empty_search(self):
        chunks = self._make_chunks(1)
        embeddings = self._make_embeddings(1)

        store = VectorStore("single-test")
        store.build(chunks, embeddings)

        results = store.search(embeddings[0], top_k=5)
        assert len(results) == 1  # Only 1 chunk exists
