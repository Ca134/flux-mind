from __future__ import annotations

from tools.context import ToolContext, ToolResult
from tools.shared.session_state import get_missing_parameters, get_recorded_parameters


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    missing = get_missing_parameters(context.session)
    context.exp_logger.log_missing_params(
        missing_params=missing,
        recorded_params=list(get_recorded_parameters(context.session).keys()),
        round_number=context.session["round_num"],
    )
    return ToolResult(return_value=str(missing))
