from __future__ import annotations

from .classify_importance import classify_importance
from tools.context import ToolContext, ToolResult


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    param_name = arguments.get("param_name", "")
    importance = classify_importance(param_name)
    return ToolResult(return_value=f"Importance of '{param_name}': {importance}")
