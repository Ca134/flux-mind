from __future__ import annotations

from .back_rag import retrieve_from_faiss


def query_knowledge_base(query: str, top_k: int = 3) -> list[dict]:
    return retrieve_from_faiss(query, top_k=top_k)
