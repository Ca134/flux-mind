from __future__ import annotations

from tools.context import ToolContext, ToolResult
from .retriever import query_knowledge_base


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    query = arguments.get("query", "")
    results = query_knowledge_base(query, top_k=3)
    context.exp_logger.log_rag_retrieval(
        query_text=query,
        results=results,
        round_number=context.session["round_num"],
    )
    content = "".join(f"Text: {item['text']}\n" for item in results)
    return ToolResult(return_value=content)
