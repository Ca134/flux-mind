from __future__ import annotations

from collections import OrderedDict
from uuid import uuid4

import numpy as np

from .config import settings
from .design_space import filter_by_user_params, get_design_space
from .model_runtime import runtime
from .pareto_utils import epsilon_pareto_front, select_representatives, weighted_filter

RESULT_CACHE_LIMIT = settings.optimization_cache_size
_results_cache: OrderedDict[str, np.ndarray] = OrderedDict()


PREFERENCE_MAP = {
    '体积': 'volume',
    '损耗': 'loss',
    '紧凑': 'compact',
    'volume': 'volume',
    'loss': 'loss',
    'compact': 'compact',
    'default': 'default',
}


def _normalize_preference(preference: str | None) -> str:
    if not preference:
        return 'default'
    return PREFERENCE_MAP.get(preference, 'default')


def _compute_derived_values(x_values: np.ndarray, y_values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    dc1, dc2, ht = x_values[:, 0], x_values[:, 1], x_values[:, 2]
    nx, ny, c = x_values[:, 4], x_values[:, 5], x_values[:, 6]
    pw, pc = y_values[:, 1], y_values[:, 2]

    width = dc1 + 0.7 * 4 + nx * c * 2 + dc2 * 2
    length = dc1 + 0.7 * 2 + nx * c * 2
    height = ny * c + 0.7 * 2 + ht * 2

    volume = width * length * height
    footprint = width * length
    total_loss = pw + pc
    return volume.astype(np.float32), footprint.astype(np.float32), total_loss.astype(np.float32)


def _apply_target_filter(x_values: np.ndarray, y_values: np.ndarray, user_params: dict) -> tuple[np.ndarray, np.ndarray]:
    if 'L' in user_params:
        inductance_spec = user_params['L']
        if isinstance(inductance_spec, dict):
            inductance_min = float(inductance_spec.get('min', 0))
            inductance_max = float(inductance_spec.get('max', 1e9))
        else:
            inductance_min = float(inductance_spec) * 0.9
            inductance_max = float(inductance_spec) * 1.1
        mask = (y_values[:, 0] >= inductance_min) & (y_values[:, 0] <= inductance_max)
        x_values, y_values = x_values[mask], y_values[mask]
        print(
            f'[ANN API] After L filtering [{inductance_min:.2f}, {inductance_max:.2f}] -> {len(x_values)} rows',
            flush=True,
        )
    return x_values, y_values


def _apply_loss_filter(
    x_values: np.ndarray,
    y_values: np.ndarray,
    volume: np.ndarray,
    footprint: np.ndarray,
    total_loss: np.ndarray,
    user_params: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if 'P' not in user_params:
        return x_values, y_values, volume, footprint, total_loss

    loss_spec = user_params['P']
    if isinstance(loss_spec, dict):
        loss_min = float(loss_spec.get('min', 0))
        loss_max = float(loss_spec.get('max', 1e9))
    else:
        loss_min = float(loss_spec) * 0.9
        loss_max = float(loss_spec) * 1.1

    mask = (total_loss >= loss_min) & (total_loss <= loss_max)
    x_values = x_values[mask]
    y_values = y_values[mask]
    volume = volume[mask]
    footprint = footprint[mask]
    total_loss = total_loss[mask]
    print(f'[ANN API] After P filtering [{loss_min:.2f}, {loss_max:.2f}] -> {len(x_values)} rows', flush=True)
    return x_values, y_values, volume, footprint, total_loss


def _format_design_row(rank: int, label: str | None, row: np.ndarray) -> dict:
    design = {
        'rank': rank,
        'params': {
            'dc1': float(row[0]),
            'dc2': float(row[1]),
            'ht': float(row[2]),
            'lg1': float(row[3]),
            'Nx': int(row[4]),
            'Ny': int(row[5]),
            'c': float(row[6]),
            'f': float(row[7]),
            'i': float(row[8]),
        },
        'performance': {
            'L': round(float(row[9]), 2),
            'Pw': round(float(row[10]), 2),
            'Pc': round(float(row[11]), 2),
            'V': round(float(row[12]), 1),
            'S': round(float(row[13]), 1),
            'P': round(float(row[14]), 2),
        },
    }
    if label is not None:
        design['type'] = label
    return design


def _store_results(results: np.ndarray) -> str:
    result_id = uuid4().hex
    _results_cache[result_id] = results.astype(np.float32, copy=False)
    while len(_results_cache) > RESULT_CACHE_LIMIT:
        _results_cache.popitem(last=False)
    return result_id


def optimize(user_params: dict, batch_size: int | None = None) -> dict:
    design_space = get_design_space(user_params)
    filtered_inputs = filter_by_user_params(design_space, user_params)
    if len(filtered_inputs) == 0:
        return {'status': 'error', 'message': 'No matching designs found'}

    print(f'[ANN API] Optimization candidates after param filter: {len(filtered_inputs)}', flush=True)
    predictions = runtime.predict(filtered_inputs, batch_size=batch_size or settings.default_batch_size)
    filtered_inputs, predictions = _apply_target_filter(filtered_inputs, predictions, user_params)
    if len(filtered_inputs) == 0:
        return {'status': 'error', 'message': 'No designs found after L filtering'}

    volume, footprint, total_loss = _compute_derived_values(filtered_inputs, predictions)
    filtered_inputs, predictions, volume, footprint, total_loss = _apply_loss_filter(
        filtered_inputs,
        predictions,
        volume,
        footprint,
        total_loss,
        user_params,
    )
    if len(filtered_inputs) == 0:
        return {'status': 'error', 'message': 'No designs found after P filtering'}

    results = np.column_stack([filtered_inputs, predictions, volume, footprint, total_loss]).astype(np.float32)
    pareto_indices = epsilon_pareto_front(total_loss, volume, epsilon=0.05)
    print(f'[ANN API] Pareto front size: {len(pareto_indices)}', flush=True)
    representatives = select_representatives(results, pareto_indices)
    result_id = _store_results(results)

    top_designs = [
        _format_design_row(index + 1, representative['label'], representative['data'])
        for index, representative in enumerate(representatives)
    ]

    return {
        'status': 'success',
        'result_id': result_id,
        'total_candidates': int(len(filtered_inputs)),
        'pareto_count': int(len(pareto_indices)),
        'top_designs': top_designs,
    }


def rerank(result_id: str, preference: str = 'default', strength: str = 'medium', top_n: int = 10) -> dict:
    if result_id not in _results_cache:
        return {'status': 'error', 'message': 'Optimization result cache expired or was not found'}

    results = _results_cache[result_id]
    normalized_preference = _normalize_preference(preference)
    top_indices = weighted_filter(results, normalized_preference, strength, top_n)
    designs = [_format_design_row(index + 1, None, results[result_index]) for index, result_index in enumerate(top_indices)]
    return {'status': 'success', 'result_id': result_id, 'designs': designs}
