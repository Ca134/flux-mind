from __future__ import annotations

from tools.context import ToolContext, ToolResult
from tools.shared.session_state import count_parameters_by_group, get_recorded_parameters


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    recorded = get_recorded_parameters(context.session)
    counts = count_parameters_by_group(context.session)
    return ToolResult(
        return_value={
            "total": len(recorded),
            "design": counts["design"],
            "operating": counts["operating"],
            "target": counts["target"],
        }
    )
