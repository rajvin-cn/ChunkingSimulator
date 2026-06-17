from __future__ import annotations
from typing import Any
import numpy as np
from .base_chunker import BaseChunker, Embedder
from .document import ParsedPage, ChunkResult


class SemanticChunker(BaseChunker):
    def __init__(self, embedder: Embedder, chunk_size: int = 256, similarity_threshold: float = 0.25) -> None:
        super().__init__()
        self.embedder = embedder
        self.chunk_size = chunk_size
        self.similarity_threshold = similarity_threshold

    def _cosine_sim(self, a: list[float], b: list[float]) -> float:
        a_arr = np.array(a, dtype=np.float64)
        b_arr = np.array(b, dtype=np.float64)
        dot = float(np.dot(a_arr, b_arr))
        na, nb = float(np.linalg.norm(a_arr)), float(np.linalg.norm(b_arr))
        return 0.0 if na == 0 or nb == 0 else dot / (na * nb)

    def _compute_centroid(self, vecs: list[list[float]]) -> list[float]:
        return list(np.mean(np.array(vecs, dtype=np.float64), axis=0))

    def chunk(self, pages: list[ParsedPage]) -> list[ChunkResult]:
        results: list[ChunkResult] = []
        chunk_index = 0
        for page in pages:
            sentences = self._split_sentences(page.content)
            if len(sentences) < 2:
                if sentences:
                    results.append(ChunkResult(
                        chunk_text=sentences[0],
                        token_count=self.count_tokens(sentences[0]),
                        chunk_index=chunk_index, page_number=page.page_number,
                        source_uri=page.source_uri, chunk_strategy="semantic",
                    ))
                    chunk_index += 1
                continue
            vecs = self.embedder.embed(sentences)
            buffer_sentences = [sentences[0]]
            buffer_vecs = [vecs[0]]
            centroid = list(vecs[0])
            for i in range(1, len(sentences)):
                sim = self._cosine_sim(vecs[i], centroid)
                buffer_tokens = self.count_tokens(" ".join(buffer_sentences))
                next_tokens = self.count_tokens(sentences[i])
                if buffer_tokens + next_tokens > self.chunk_size or (buffer_sentences and sim < self.similarity_threshold):
                    reason = "token_limit" if buffer_tokens + next_tokens > self.chunk_size else "topic_shift"
                    results.append(ChunkResult(
                        chunk_text=" ".join(buffer_sentences),
                        token_count=buffer_tokens,
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        source_uri=page.source_uri,
                        chunk_strategy="semantic",
                        reason=reason,
                    ))
                    chunk_index += 1
                    buffer_sentences = [sentences[i]]
                    buffer_vecs = [vecs[i]]
                    centroid = list(vecs[i])
                else:
                    buffer_sentences.append(sentences[i])
                    buffer_vecs.append(vecs[i])
                    centroid = self._compute_centroid(buffer_vecs)
            if buffer_sentences:
                results.append(ChunkResult(
                    chunk_text=" ".join(buffer_sentences),
                    token_count=self.count_tokens(" ".join(buffer_sentences)),
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    source_uri=page.source_uri,
                    chunk_strategy="semantic",
                ))
                chunk_index += 1
        return results
