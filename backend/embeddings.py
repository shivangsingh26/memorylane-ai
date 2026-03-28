"""
Chroma vector store with OpenAI embeddings (text-embedding-3-small).

Retrieval strategies:
  query()           — semantic top-k (for chat)
  mmr_query()       — Maximal Marginal Relevance: relevant + diverse (for chat)
  temporal_spread() — chunks spread across the full timeline (for timeline/roast)
  random_sample()   — truly random chunks, different every call (for story/quiz)
  multi_query()     — several seed queries merged + deduplicated (for quiz)
"""

import json
import math
import random
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
    # Public retrieval API
    # ------------------------------------------------------------------

    def query(self, text: str, n_results: int = None) -> list[dict]:
        """Standard semantic top-k search."""
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
        return self._format_results(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )

    def mmr_query(self, text: str, n_results: int = 6, fetch_k: int = 30, diversity: float = 0.6) -> list[dict]:
        """
        Maximal Marginal Relevance — balances relevance with diversity.
        diversity=0.0 → pure relevance, diversity=1.0 → pure diversity.
        Fetches fetch_k candidates, then greedily picks n_results diverse ones.
        """
        count = self._collection.count()
        if count == 0:
            return []

        fetch_k = min(fetch_k, count)
        n_results = min(n_results, fetch_k)
        query_emb = self._embed_texts([text])[0]

        # Fetch a wider candidate pool
        results = self._collection.query(
            query_embeddings=[query_emb],
            n_results=fetch_k,
            include=["documents", "metadatas", "distances", "embeddings"],
        )
        docs      = results["documents"][0]
        metas     = results["metadatas"][0]
        dists     = results["distances"][0]
        doc_embs  = results["embeddings"][0]  # list of embedding vectors

        # Convert cosine distance to similarity
        rel_scores = [1 - d for d in dists]

        selected_idx = []
        remaining    = list(range(len(docs)))

        for _ in range(n_results):
            if not remaining:
                break
            if not selected_idx:
                # First pick: most relevant
                best = max(remaining, key=lambda i: rel_scores[i])
            else:
                # MMR score: relevance - diversity_penalty
                def mmr_score(i: int) -> float:
                    rel = rel_scores[i]
                    max_sim = max(
                        self._cosine_sim(doc_embs[i], doc_embs[j])
                        for j in selected_idx
                    )
                    return (1 - diversity) * rel - diversity * max_sim

                best = max(remaining, key=mmr_score)

            selected_idx.append(best)
            remaining.remove(best)

        return self._format_results(
            [docs[i] for i in selected_idx],
            [metas[i] for i in selected_idx],
            [dists[i] for i in selected_idx],
        )

    def temporal_spread(self, n_periods: int = 5, per_period: int = 3) -> list[dict]:
        """
        Divide the full timeline into n_periods equal buckets and randomly
        sample per_period chunks from each. Guarantees chronological diversity.
        """
        count = self._collection.count()
        if count == 0:
            return []

        # Pull all IDs and their offsets in insertion order
        all_ids = self._collection.get(include=[])["ids"]
        total = len(all_ids)
        period_size = max(1, total // n_periods)

        selected_ids = []
        for p in range(n_periods):
            start = p * period_size
            end   = start + period_size if p < n_periods - 1 else total
            bucket = all_ids[start:end]
            k = min(per_period, len(bucket))
            selected_ids.extend(random.sample(bucket, k))

        results = self._collection.get(
            ids=selected_ids,
            include=["documents", "metadatas"],
        )
        chunks = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            chunks.append(self._fmt_chunk(doc, meta))

        # Sort by start_time so narrative order is preserved
        chunks.sort(key=lambda c: c["start_time"])
        return chunks

    def random_sample(self, n: int = 15) -> list[dict]:
        """
        Truly random sample — uses a random offset so it's different every call.
        Solves the 'always same early chunks' problem with Chroma's get().
        """
        count = self._collection.count()
        if count == 0:
            return []
        n = min(n, count)

        # Random offset into the collection
        offset = random.randint(0, max(0, count - n * 3))
        fetch  = min(n * 3, count - offset)

        results = self._collection.get(
            limit=fetch,
            offset=offset,
            include=["documents", "metadatas"],
        )
        docs  = results["documents"]
        metas = results["metadatas"]

        # Randomly pick n from the fetched pool
        indices = random.sample(range(len(docs)), min(n, len(docs)))
        return [self._fmt_chunk(docs[i], metas[i]) for i in indices]

    def multi_query(self, queries: list[str], n_per_query: int = 4) -> list[dict]:
        """
        Run multiple semantic queries and merge results, deduplicating by text.
        Used by quiz mode to get diverse question material.
        """
        seen_texts: set[str] = set()
        all_chunks: list[dict] = []

        for q in queries:
            chunks = self.query(q, n_results=n_per_query)
            for c in chunks:
                key = c["text"][:80]
                if key not in seen_texts:
                    seen_texts.add(key)
                    all_chunks.append(c)

        # Shuffle so order doesn't bias the LLM
        random.shuffle(all_chunks)
        return all_chunks

    def store_messages(self, messages: list[dict]) -> int:
        """Chunk messages, embed, and upsert into Chroma. Returns chunk count."""
        chunks = chunk_messages(messages, settings.chunk_size)
        if not chunks:
            return 0

        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch    = chunks[i : i + batch_size]
            texts    = [c["text"] for c in batch]
            ids      = [c["id"] for c in batch]
            metadatas = [
                {
                    "start_time":    c["start_time"] or "",
                    "end_time":      c["end_time"] or "",
                    "senders":       json.dumps(c["senders"]),
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
                time.sleep(0.3)

        return len(chunks)

    def is_empty(self) -> bool:
        return self._collection.count() == 0

    def clear(self) -> None:
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

    @staticmethod
    def _cosine_sim(a: list[float], b: list[float]) -> float:
        dot  = sum(x * y for x, y in zip(a, b))
        norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b))
        return dot / norm if norm else 0.0

    @staticmethod
    def _fmt_chunk(doc: str, meta: dict) -> dict:
        return {
            "text":       doc,
            "start_time": meta.get("start_time", ""),
            "end_time":   meta.get("end_time", ""),
            "senders":    json.loads(meta.get("senders", "[]")),
        }

    def _format_results(
        self,
        docs:   list[str],
        metas:  list[dict],
        dists:  list[float],
    ) -> list[dict]:
        return [
            {
                **self._fmt_chunk(doc, meta),
                "similarity": round(1 - dist, 4),
            }
            for doc, meta, dist in zip(docs, metas, dists)
        ]
