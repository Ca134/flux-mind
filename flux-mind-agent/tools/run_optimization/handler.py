from __future__ import annotations

from tools.context import ToolContext, ToolResult
from tools.shared.session_state import can_run_optimization, count_parameters_by_group, get_recorded_parameters
from .service import INVALID_TRIGGER_MESSAGE, execute_optimization


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    if not can_run_optimization(context.session):
        result = {
            'status': 'error',
            'message': INVALID_TRIGGER_MESSAGE,
            'counts': count_parameters_by_group(context.session),
        }
        context.send_to_frontend(context.socket_id, 'error', result['message'])
        return ToolResult(return_value=result, purpose='run_optimization blocked by missing prerequisites')

    user_params = get_recorded_parameters(context.session)
    context.session['optimization_triggered'] = True
    context.exp_logger.log_optimization_triggered(
        user_params=user_params,
        round_number=context.session['round_num'],
    )
    result = execute_optimization(context.session)
    if result.get('status') == 'success':
        context.session['optimization_success'] = True
        context.session['optimization_result_id'] = result.get('result_id')
        context.exp_logger.log_optimization_result(
            total_candidates=result.get('total_candidates', 0),
            pareto_count=result.get('pareto_count', 0),
            representatives=result.get('top_designs', []),
        )
    context.send_to_frontend(context.socket_id, 'design_result', result)
    return ToolResult(return_value=result)
