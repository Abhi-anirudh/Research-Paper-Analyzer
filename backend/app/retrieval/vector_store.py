"""FAISS vector store — stores and retrieves chunk embeddings per paper."""

import os
import json
import numpy as np
import faiss
from app.config import get_settings
from app.models.schemas import Chunk


class VectorStore:
    """Manages FAISS indices for paper chunks."""

    def __init__(self, paper_id: str):
        self.paper_id = paper_id
        self.settings = get_settings()
        self.index: faiss.Index | None = None
        self.chunks: list[Chunk] = []
        self._index_path = os.path.join(self.settings.index_dir, f"{paper_id}.faiss")
        self._meta_path = os.path.join(self.settings.index_dir, f"{paper_id}.json")

    def build(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        """Build a new FAISS index from chunks and their embeddings."""
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner product on normalized vectors = cosine
        self.index.add(embeddings)
        self.chunks = chunks
        self._save()

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[tuple[Chunk, float]]:
        """Search for the top-k most similar chunks.

        Returns:
            List of (chunk, similarity_score) tuples sorted by descending score.
        """
        self._load()
        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = np.array([query_embedding], dtype=np.float32)
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append((self.chunks[idx], float(score)))

        return results

    def _save(self) -> None:
        """Persist index and metadata to disk."""
        os.makedirs(os.path.dirname(self._index_path), exist_ok=True)
        faiss.write_index(self.index, self._index_path)

        meta = [chunk.model_dump() for chunk in self.chunks]
        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    def _load(self) -> None:
        """Load index and metadata from disk if not already loaded."""
        if self.index is not None:
            return

        if not os.path.exists(self._index_path):
            raise FileNotFoundError(f"No index found for paper_id={self.paper_id}")

        self.index = faiss.read_index(self._index_path)

        with open(self._meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.chunks = [Chunk(**m) for m in meta]

    def exists(self) -> bool:
        """Check if an index exists on disk for this paper."""
        return os.path.exists(self._index_path)
