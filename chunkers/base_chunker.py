from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Protocol
from .document import ParsedPage, ChunkResult


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class BaseChunker(ABC):
    def __init__(self) -> None:
        self._encoder: Any = None

    def count_tokens(self, text: str) -> int:
        import tiktoken
        if self._encoder is None:
            self._encoder = tiktoken.get_encoding("cl100k_base")
        return len(self._encoder.encode(text))

    @abstractmethod
    def chunk(self, pages: list[ParsedPage]) -> list[ChunkResult]: ...

    def _split_sentences(self, text: str) -> list[str]:
        import re
        text = text.replace("\n", " ").strip()
        parts = re.split(r"(?<=[.!?])\s+", text)
        return [p.strip() for p in parts if p.strip()]
