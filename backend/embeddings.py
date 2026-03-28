"""
Chroma vector store with OpenAI embeddings (text-embedding-3-small).
"""

import json
import time
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI
from config import settings
from data_processor import chunk_messages

COLLECTION_NAME = "couple_chat"


class EmbeddingStore:
    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._openai = OpenAI(api_key=settings.openai_api_key)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store_messages(self, messages: list[dict]) -> int:
        """Chunk messages, embed, and upsert into Chroma. Returns chunk count."""
        chunks = chunk_messages(messages, settings.chunk_size)
        if not chunks:
            return 0

        # Chroma upsert in batches to avoid rate limits
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c["text"] for c in batch]
            ids = [c["id"] for c in batch]
            metadatas = [
                {
                    "start_time": c["start_time"] or "",
                    "end_time": c["end_time"] or "",
                    "senders": json.dumps(c["senders"]),
                    "message_count": c["message_count"],
                }
                for c in batch
            ]
            embeddings = self._embed_texts(texts)
            self._collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            if i + batch_size < len(chunks):
                time.sleep(0.3)  # be gentle with the API

        return len(chunks)

    def query(self, text: str, n_results: int = None) -> list[dict]:
        """Return top-k similar chunks with metadata."""
        n_results = n_results or settings.rag_top_k
        count = self._collection.count()
        if count == 0:
            return []

        n_results = min(n_results, count)
        embedding = self._embed_texts([text])[0]
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(
                {
                    "text": doc,
                    "start_time": meta.get("start_time", ""),
                    "end_time": meta.get("end_time", ""),
                    "senders": json.loads(meta.get("senders", "[]")),
                    "similarity": round(1 - dist, 4),
                }
            )
        return chunks

    def sample_chunks(self, n: int = 20) -> list[dict]:
        """Return up to n random chunks (used for features that need broad context)."""
        count = self._collection.count()
        if count == 0:
            return []
        n = min(n, count)
        results = self._collection.get(limit=n, include=["documents", "metadatas"])
        chunks = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            chunks.append(
                {
                    "text": doc,
                    "start_time": meta.get("start_time", ""),
                    "end_time": meta.get("end_time", ""),
                }
            )
        return chunks

    def is_empty(self) -> bool:
        return self._collection.count() == 0

    def clear(self) -> None:
        """Delete all stored vectors."""
        self._client.delete_collection(COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._openai.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]
