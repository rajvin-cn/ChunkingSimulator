from __future__ import annotations

import json
import os
from typing import Any

from chunkers import ParsedPage


class LocalEmbedder:
    _model = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return vecs.tolist()


class EURIEmbedder:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self._url = f"{base_url.rstrip('/')}/embeddings"
        self._model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self._client: Any = None
        self._batch_size = 100

    def embed(self, texts: list[str]) -> list[list[float]]:
        from httpx import Client

        if self._client is None:
            self._client = Client(timeout=60.0)

        all_vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start:start + self._batch_size]
            response = self._client.post(
                self._url,
                json={"input": batch, "model": self._model},
                headers=self._headers,
            )
            response.raise_for_status()
            data: list[dict[str, Any]] = response.json()["data"]
            data.sort(key=lambda d: d["index"])
            all_vectors.extend(d["embedding"] for d in data)

        return all_vectors


ENGINE_DEFAULTS = {
    "local": {
        "similarity_threshold": 0.25,
        "chunk_size": 256,
        "label": "Local (sentence-transformers)",
    },
    "euri": {
        "similarity_threshold": 0.5,
        "chunk_size": 512,
        "label": "Remote (EURI API)",
    },
}


def init_embedder(engine: str, api_key: str = "", base_url: str = "", model: str = "") -> Any:
    if engine == "euri":
        key = api_key or os.environ.get("EURI_API_KEY", "")
        url = base_url or os.environ.get("EURI_BASE_URL", "https://api.euron.one/api/v1/euri")
        mdl = model or os.environ.get("EURI_EMBEDDING_MODEL", "gemini-embedding-2")
        return EURIEmbedder(api_key=key, base_url=url, model=mdl)
    return LocalEmbedder()


def make_page(text: str, page_number: int = 1) -> ParsedPage:
    return ParsedPage(
        page_number=page_number,
        content=text,
        source_uri="visualizer/demo.txt",
    )


def vector_preview(vec: list[float], show: int = 3) -> str:
    vals = [f"{v:.4f}" for v in vec[:show]]
    return f"[{', '.join(vals)}, ...] ({len(vec)}-dim)"


def escape_html(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))


def merge_small_chunks(items: list[dict], min_tokens: int) -> list[dict]:
    if min_tokens <= 0 or len(items) < 2:
        return items
    result = [items[0].copy()]
    for item in items[1:]:
        if result[-1]["token_count"] < min_tokens:
            result[-1]["chunk_text"] += " " + item["chunk_text"]
            result[-1]["token_count"] += item["token_count"]
        else:
            result.append(item.copy())
    return result
