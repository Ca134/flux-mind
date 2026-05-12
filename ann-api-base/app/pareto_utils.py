from __future__ import annotations

import numpy as np

WEIGHT_CONFIGS = {
    ('default', None): (0.4, 0.4, 0.2),
    ('loss', 'light'): (0.5, 0.35, 0.15),
    ('loss', 'medium'): (0.6, 0.25, 0.15),
    ('loss', 'strong'): (0.8, 0.15, 0.05),
    ('volume', 'light'): (0.35, 0.5, 0.15),
    ('volume', 'medium'): (0.25, 0.6, 0.15),
    ('volume', 'strong'): (0.15, 0.8, 0.05),
    ('compact', 'light'): (0.35, 0.35, 0.3),
    ('compact', 'medium'): (0.3, 0.3, 0.4),
    ('compact', 'strong'): (0.2, 0.2, 0.6),
}


def epsilon_pareto_front(p: np.ndarray, volume: np.ndarray, epsilon: float = 0.05) -> list[int]:
    p = np.asarray(p, dtype=np.float64)
    volume = np.asarray(volume, dtype=np.float64)
    count = len(p)
    if count == 0:
        return []

    order = np.argsort(p)
    p_sorted = p[order]
    v_sorted = volume[order]
    is_pareto = np.ones(count, dtype=bool)
    min_volume = np.inf

    for index in range(count):
        if v_sorted[index] > min_volume:
            is_pareto[index] = False
        else:
            min_volume = min(min_volume, v_sorted[index] * (1 - epsilon))

    pareto_mask = is_pareto.copy()
    pareto_p = p_sorted[pareto_mask]
    pareto_v = v_sorted[pareto_mask]
    pareto_positions = np.where(pareto_mask)[0]
    final_pareto = np.ones(len(pareto_p), dtype=bool)

    for i in range(len(pareto_p)):
        if not final_pareto[i]:
            continue
        for j in range(len(pareto_p)):
            if i == j or not final_pareto[j]:
                continue
            p_better = pareto_p[j] <= pareto_p[i] * (1 + epsilon)
            v_better = pareto_v[j] <= pareto_v[i] * (1 + epsilon)
            p_strict = pareto_p[j] < pareto_p[i] * (1 - epsilon)
            v_strict = pareto_v[j] < pareto_v[i] * (1 - epsilon)
            if p_better and v_better and (p_strict or v_strict):
                final_pareto[i] = False
                break

    result_indices = order[pareto_positions[final_pareto]]
    return sorted(result_indices.tolist())


def select_representatives(results: np.ndarray, pareto_indices: list[int]) -> list[dict]:
    pareto = results[pareto_indices]
    p_values = pareto[:, 14]
    volume_values = pareto[:, 12]
    footprint_values = pareto[:, 13]
    copper_loss_values = pareto[:, 10]

    representatives: list[dict] = []

    min_loss_index = int(np.argmin(p_values))
    representatives.append({'type': 'min_loss', 'label': 'Lowest Loss', 'index': pareto_indices[min_loss_index], 'data': pareto[min_loss_index]})

    min_volume_index = int(np.argmin(volume_values))
    representatives.append({'type': 'min_volume', 'label': 'Smallest Volume', 'index': pareto_indices[min_volume_index], 'data': pareto[min_volume_index]})

    p_norm = (p_values - p_values.min()) / (p_values.max() - p_values.min() + 1e-9)
    v_norm = (volume_values - volume_values.min()) / (volume_values.max() - volume_values.min() + 1e-9)
    distance = np.sqrt(p_norm ** 2 + v_norm ** 2)
    balanced_index = int(np.argmin(distance))
    representatives.append({'type': 'balanced', 'label': 'Balanced', 'index': pareto_indices[balanced_index], 'data': pareto[balanced_index]})

    efficiency_ratio = copper_loss_values / (p_values + 1e-9)
    efficiency_index = int(np.argmin(efficiency_ratio))
    representatives.append({'type': 'high_efficiency', 'label': 'High Efficiency', 'index': pareto_indices[efficiency_index], 'data': pareto[efficiency_index]})

    compact_index = int(np.argmin(footprint_values))
    representatives.append({'type': 'compact', 'label': 'Compact', 'index': pareto_indices[compact_index], 'data': pareto[compact_index]})

    return representatives


def weighted_filter(results: np.ndarray, preference: str = 'default', strength: str | None = None, top_n: int = 10) -> list[int]:
    p_values = results[:, 14]
    volume_values = results[:, 12]
    footprint_values = results[:, 13]

    key = (preference, strength)
    if key not in WEIGHT_CONFIGS:
        key = ('default', None)
    weight_p, weight_v, weight_s = WEIGHT_CONFIGS[key]

    p_norm = (p_values - p_values.min()) / (p_values.max() - p_values.min() + 1e-9)
    v_norm = (volume_values - volume_values.min()) / (volume_values.max() - volume_values.min() + 1e-9)
    s_norm = (footprint_values - footprint_values.min()) / (footprint_values.max() - footprint_values.min() + 1e-9)

    score = weight_p * p_norm + weight_v * v_norm + weight_s * s_norm
    return np.argsort(score)[:top_n].tolist()
