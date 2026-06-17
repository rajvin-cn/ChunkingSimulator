from __future__ import annotations
from pydantic import BaseModel, Field


class ParsedPage(BaseModel):
    page_number: int = 0
    content: str = ""
    source_uri: str = ""


class ChunkResult(BaseModel):
    chunk_text: str
    token_count: int = 0
    chunk_index: int = 0
    page_number: int = 0
    source_uri: str | None = None
    chunk_strategy: str = ""
    parent_chunk_id: str | None = None
    chunk_embedding: list[float] | None = None
    full_page_embedding: list[float] | None = None
    reason: str | None = None
