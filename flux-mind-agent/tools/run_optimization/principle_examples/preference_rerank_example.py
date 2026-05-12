"""Example only: rerank cached designs with user preference weights."""

from __future__ import annotations

import numpy as np

WEIGHTS = {
    'default': (0.4, 0.4, 0.2),
    'loss': (0.7, 0.2, 0.1),
    'volume': (0.2, 0.7, 0.1),
    'compact': (0.2, 0.2, 0.6),
}


def rerank(results: np.ndarray, preference: str = 'default', top_n: int = 5) -> list[int]:
    weight_loss, weight_volume, weight_footprint = WEIGHTS.get(preference, WEIGHTS['default'])
    loss_values = results[:, 14]
    volume_values = results[:, 12]
    footprint_values = results[:, 13]

    loss_norm = (loss_values - loss_values.min()) / (loss_values.max() - loss_values.min() + 1e-9)
    volume_norm = (volume_values - volume_values.min()) / (volume_values.max() - volume_values.min() + 1e-9)
    footprint_norm = (footprint_values - footprint_values.min()) / (footprint_values.max() - footprint_values.min() + 1e-9)

    score = weight_loss * loss_norm + weight_volume * volume_norm + weight_footprint * footprint_norm
    return np.argsort(score)[:top_n].tolist()
