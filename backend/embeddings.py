"""
Chroma vector store with OpenAI embeddings (text-embedding-3-small).

Retrieval strategies:
  mmr_query()          — Maximal Marginal Relevance (relevant + diverse) — for chat
  month_spread()       — Sample from every calendar month equally — for timeline/roast/story
  random_sample()      — Truly random, different every call — for story variety
  multi_query()        — Multiple semantic queries merged + deduplicated — for quiz
"""

import json
import math
import random
import time
from collections import defaultdict
import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI
from config import settings
from data_processor import chunk_messages  # noqa: F401 used by store_messages

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
        # Cached month → [ids] index, built lazily
        self._month_index: dict[str, list[str]] | None = None

    # ------------------------------------------------------------------
    # Public retrieval API
    # ------------------------------------------------------------------

    def query(self, text: str, n_results: int = None) -> list[dict]:
        """Standard semantic top-k."""
        n_results = n_results or settings.rag_top_k
        count = self._collection.count()
        if count == 0:
            return []
        n_results = min(n_results, count)
        emb = self._embed_texts([text])[0]
        results = self._collection.query(
            query_embeddings=[emb],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        return self._format_results(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )

    def mmr_query(
        self,
        text: str,
        n_results: int = 6,
        fetch_k: int = 30,
        diversity: float = 0.55,
    ) -> list[dict]:
        """
        Maximal Marginal Relevance — relevant AND diverse.
        diversity=0 → pure relevance, 1 → pure diversity.
        """
        count = self._collection.count()
        if count == 0:
            return []
        fetch_k  = min(fetch_k, count)
        n_results = min(n_results, fetch_k)
        query_emb = self._embed_texts([text])[0]

        results = self._collection.query(
            query_embeddings=[query_emb],
            n_results=fetch_k,
            include=["documents", "metadatas", "distances", "embeddings"],
        )
        docs     = results["documents"][0]
        metas    = results["metadatas"][0]
        dists    = results["distances"][0]
        doc_embs = results["embeddings"][0]
        rel      = [1 - d for d in dists]

        selected, remaining = [], list(range(len(docs)))
        for _ in range(n_results):
            if not remaining:
                break
            if not selected:
                best = max(remaining, key=lambda i: rel[i])
            else:
                def _score(i: int) -> float:
                    max_sim = max(
                        self._cosine_sim(doc_embs[i], doc_embs[j])
                        for j in selected
                    )
                    return (1 - diversity) * rel[i] - diversity * max_sim
                best = max(remaining, key=_score)
            selected.append(best)
            remaining.remove(best)

        return self._format_results(
            [docs[i] for i in selected],
            [metas[i] for i in selected],
            [dists[i] for i in selected],
        )

    def month_spread(self, per_month: int = 2, max_months: int = 9) -> list[dict]:
        """
        Sample `per_month` random chunks from EACH calendar month.
        This is the correct way to get true chronological diversity —
        it doesn't oversample October just because it has 5x more chunks.
        """
        index = self._get_month_index()
        if not index:
            return []

        months = sorted(index.keys())
        # If more months than max_months, keep earliest + latest + random middle
        if len(months) > max_months:
            middle = random.sample(months[1:-1], max_months - 2)
            months = [months[0]] + sorted(middle) + [months[-1]]

        selected_ids = []
        for month in months:
            pool = index[month]
            k    = min(per_month, len(pool))
            selected_ids.extend(random.sample(pool, k))

        if not selected_ids:
            return []

        results = self._collection.get(
            ids=selected_ids,
            include=["documents", "metadatas"],
        )
        chunks = [
            self._fmt_chunk(doc, meta)
            for doc, meta in zip(results["documents"], results["metadatas"])
        ]
        # Sort chronologically so narrative makes sense
        chunks.sort(key=lambda c: c["start_time"])
        return chunks

    def random_sample(self, n: int = 15) -> list[dict]:
        """
        Truly random sample — random month first, then random chunks within it.
        Different every call regardless of collection size.
        """
        index = self._get_month_index()
        if not index:
            return []

        all_ids: list[str] = []
        months = list(index.keys())
        random.shuffle(months)
        for month in months:
            pool = index[month]
            k    = min(max(1, n // len(months)), len(pool))
            all_ids.extend(random.sample(pool, k))
            if len(all_ids) >= n * 2:
                break

        selected = random.sample(all_ids, min(n, len(all_ids)))
        results  = self._collection.get(
            ids=selected,
            include=["documents", "metadatas"],
        )
        return [
            self._fmt_chunk(doc, meta)
            for doc, meta in zip(results["documents"], results["metadatas"])
        ]

    def multi_query(self, queries: list[str], n_per_query: int = 4) -> list[dict]:
        """
        Run multiple semantic queries, merge + deduplicate by text prefix.
        """
        seen: set[str] = set()
        out:  list[dict] = []
        for q in queries:
            for c in self.query(q, n_results=n_per_query):
                key = c["text"][:60]
                if key not in seen:
                    seen.add(key)
                    out.append(c)
        random.shuffle(out)
        return out

    def store_messages(self, messages: list[dict]) -> int:
        chunks = chunk_messages(messages, settings.chunk_size)
        if not chunks:
            return 0
        self._month_index = None  # Invalidate cache

        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch     = chunks[i : i + batch_size]
            texts     = [c["text"] for c in batch]
            ids       = [c["id"] for c in batch]
            metadatas = [
                {
                    "start_time":    c["start_time"] or "",
                    "end_time":      c["end_time"] or "",
                    "senders":       json.dumps(c["senders"]),
                    "message_count": c["message_count"],
                }
                for c in batch
            ]
            self._collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=self._embed_texts(texts),
                metadatas=metadatas,
            )
            if i + batch_size < len(chunks):
                time.sleep(0.3)

        return len(chunks)

    def is_empty(self) -> bool:
        return self._collection.count() == 0

    def clear(self) -> None:
        self._month_index = None
        self._client.delete_collection(COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Month index (cached)
    # ------------------------------------------------------------------

    def _get_month_index(self) -> dict[str, list[str]]:
        """Build and cache a month → [chunk_ids] mapping."""
        if self._month_index is not None:
            return self._month_index

        count = self._collection.count()
        if count == 0:
            self._month_index = {}
            return {}

        # Fetch all IDs + metadatas in one call
        all_data = self._collection.get(
            limit=count,
            include=["metadatas"],
        )
        index: dict[str, list[str]] = defaultdict(list)
        for cid, meta in zip(all_data["ids"], all_data["metadatas"]):
            month = meta.get("start_time", "")[:7]  # "YYYY-MM"
            if month:
                index[month].append(cid)

        self._month_index = dict(index)
        return self._month_index

    # ------------------------------------------------------------------
    # Helpers
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
        docs:  list[str],
        metas: list[dict],
        dists: list[float],
    ) -> list[dict]:
        return [
            {**self._fmt_chunk(doc, meta), "similarity": round(1 - d, 4)}
            for doc, meta, d in zip(docs, metas, dists)
        ]
