from __future__ import annotations

from tools.context import ToolContext, ToolResult
from tools.shared.session_state import get_recorded_parameters, record_parameters


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    params = arguments.get("params", {})
    success = record_parameters(context.session, params)
    if isinstance(params, dict):
        recorded = list(get_recorded_parameters(context.session).keys())
        for param_name, param_value in params.items():
            context.exp_logger.log_param_record(
                param_name=param_name,
                param_value=param_value,
                is_valid=success,
                round_number=context.session["round_num"],
                recorded_so_far=recorded,
            )
    return ToolResult(return_value=str(success))
