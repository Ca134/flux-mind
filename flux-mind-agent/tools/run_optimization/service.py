from __future__ import annotations

from .ann_api_client import optimize_via_api
from tools.shared.session_state import can_run_optimization, count_parameters_by_group, get_recorded_parameters

INVALID_TRIGGER_MESSAGE = '当前不满足优化触发条件：需要设计参数数量大于3，或至少指定一个目标参数（L/P，可为具体值或范围）。'


def execute_optimization(session: dict) -> dict:
    if not can_run_optimization(session):
        return {
            'status': 'error',
            'message': INVALID_TRIGGER_MESSAGE,
            'counts': count_parameters_by_group(session),
        }

    user_params = get_recorded_parameters(session)
    return optimize_via_api(user_params)
