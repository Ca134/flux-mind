from __future__ import annotations

from tools.context import ToolContext, ToolResult
from tools.run_optimization.ann_api_client import rerank_via_api

PREFERENCE_MAP = {
    '体积': 'volume',
    '损耗': 'loss',
    '紧凑': 'compact',
    'volume': 'volume',
    'loss': 'loss',
    'compact': 'compact',
    'default': 'default',
}


MISSING_RESULT_MESSAGE = '当前没有可重排的优化结果，请先运行一次优化设计。'


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    result_id = context.session.get('optimization_result_id')
    if not result_id:
        result = {'status': 'error', 'message': MISSING_RESULT_MESSAGE}
        context.send_to_frontend(context.socket_id, 'error', MISSING_RESULT_MESSAGE)
        return ToolResult(return_value=result, purpose='filter_by_preference blocked by missing optimization result')

    raw_preference = arguments.get('preference', 'default')
    preference = PREFERENCE_MAP.get(raw_preference, 'default')
    strength = arguments.get('strength', 'medium')
    top_n = int(arguments.get('top_n', 10))
    result = rerank_via_api(result_id=result_id, preference=preference, strength=strength, top_n=top_n)
    context.exp_logger.log_preference_rerank(
        preference_type=preference,
        strength=strength,
        results=result.get('designs', []) if isinstance(result, dict) else [],
    )
    context.send_to_frontend(context.socket_id, 'design_result', result)
    return ToolResult(return_value=result)
