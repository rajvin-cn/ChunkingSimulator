from __future__ import annotations
from .base_chunker import BaseChunker, Embedder
from .document import ParsedPage, ChunkResult


class LateChunker(BaseChunker):
    def __init__(self, embedder: Embedder, chunk_size: int = 256) -> None:
        super().__init__()
        self.embedder = embedder
        self.chunk_size = chunk_size

    def _embed_full_document(self, text: str) -> list[float]:
        return self.embedder.embed([text])[0]

    def chunk(self, pages: list[ParsedPage]) -> list[ChunkResult]:
        results: list[ChunkResult] = []
        chunk_index = 0
        full_doc_text = "\n\n".join(p.content for p in pages)
        full_doc_vec = self._embed_full_document(full_doc_text)
        for page in pages:
            sentences = self._split_sentences(page.content)
            buffers: list[str] = []
            buf: list[str] = []
            buf_tok = 0
            for s in sentences:
                tk = self.count_tokens(s)
                if buf and buf_tok + tk > self.chunk_size:
                    buffers.append(" ".join(buf))
                    buf, buf_tok = [s], tk
                else:
                    buf.append(s)
                    buf_tok += tk
            if buf:
                buffers.append(" ".join(buf))
            chunk_vecs = self.embedder.embed(buffers)
            for i, (ct, cv) in enumerate(zip(buffers, chunk_vecs)):
                results.append(ChunkResult(
                    chunk_text=ct,
                    token_count=self.count_tokens(ct),
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    source_uri=page.source_uri,
                    chunk_strategy="late",
                    chunk_embedding=cv,
                    full_document_embedding=full_doc_vec,
                ))
                chunk_index += 1
        return results
