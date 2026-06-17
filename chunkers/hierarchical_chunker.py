from __future__ import annotations
from .base_chunker import BaseChunker
from .document import ParsedPage, ChunkResult


class HierarchicalChunker(BaseChunker):
    def __init__(self, chunk_size: int = 1024, child_chunk_size: int = 128, child_overlap: int = 32) -> None:
        super().__init__()
        self.chunk_size = chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap

    def _create_children(self, parent_text: str, parent_id: str, page_number: int, source_uri: str, start_index: int) -> tuple[list[ChunkResult], int]:
        sentences = self._split_sentences(parent_text)
        children: list[ChunkResult] = []
        chunk_index = start_index
        i = 0
        while i < len(sentences):
            batch: list[str] = []
            batch_tokens = 0
            while i < len(sentences):
                st = sentences[i]
                tk = self.count_tokens(st)
                if batch_tokens + tk <= self.child_chunk_size:
                    batch.append(st)
                    batch_tokens += tk
                    i += 1
                else:
                    break
            if batch:
                child_text = " ".join(batch)
                children.append(ChunkResult(
                    chunk_text=child_text,
                    token_count=self.count_tokens(child_text),
                    chunk_index=chunk_index,
                    page_number=page_number,
                    source_uri=source_uri,
                    chunk_strategy="hierarchical",
                    parent_chunk_id=parent_id,
                ))
                chunk_index += 1
                overlap_sentences: list[str] = []
                overlap_tokens = 0
                for s in reversed(batch):
                    t = self.count_tokens(s)
                    if overlap_tokens + t <= self.child_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += t
                    else:
                        break
                if len(overlap_sentences) < len(batch):
                    i -= len(overlap_sentences)
        return children, chunk_index

    def chunk(self, pages: list[ParsedPage]) -> list[ChunkResult]:
        results: list[ChunkResult] = []
        chunk_index = 0
        for page in pages:
            sentences = self._split_sentences(page.content)
            if not sentences:
                continue
            buffer: list[str] = []
            buffer_tokens = 0
            for sent in sentences:
                sent_tokens = self.count_tokens(sent)
                if buffer and buffer_tokens + sent_tokens > self.chunk_size:
                    parent_text = " ".join(buffer)
                    parent_id = f"parent_{chunk_index}"
                    results.append(ChunkResult(
                        chunk_text=parent_text,
                        token_count=self.count_tokens(parent_text),
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        source_uri=page.source_uri,
                        chunk_strategy="hierarchical",
                        parent_chunk_id=None,
                    ))
                    chunk_index += 1
                    children, chunk_index = self._create_children(
                        parent_text, parent_id, page.page_number, page.source_uri, chunk_index,
                    )
                    results.extend(children)
                    buffer = [sent]
                    buffer_tokens = sent_tokens
                else:
                    buffer.append(sent)
                    buffer_tokens += sent_tokens
            if buffer:
                parent_text = " ".join(buffer)
                parent_id = f"parent_{chunk_index}"
                results.append(ChunkResult(
                    chunk_text=parent_text,
                    token_count=self.count_tokens(parent_text),
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    source_uri=page.source_uri,
                    chunk_strategy="hierarchical",
                    parent_chunk_id=None,
                ))
                chunk_index += 1
                children, chunk_index = self._create_children(
                    parent_text, parent_id, page.page_number, page.source_uri, chunk_index,
                )
                results.extend(children)
        return results
