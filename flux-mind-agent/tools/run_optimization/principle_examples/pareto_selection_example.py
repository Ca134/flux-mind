"""Example only: simple epsilon-Pareto selection by loss and volume."""

from __future__ import annotations

import numpy as np


def epsilon_pareto_front(loss_values: np.ndarray, volume_values: np.ndarray, epsilon: float = 0.05) -> list[int]:
    indices = []
    for i in range(len(loss_values)):
        dominated = False
        for j in range(len(loss_values)):
            if i == j:
                continue
            loss_better = loss_values[j] <= loss_values[i] * (1 + epsilon)
            volume_better = volume_values[j] <= volume_values[i] * (1 + epsilon)
            strictly_better = (
                loss_values[j] < loss_values[i] * (1 - epsilon)
                or volume_values[j] < volume_values[i] * (1 - epsilon)
            )
            if loss_better and volume_better and strictly_better:
                dominated = True
                break
        if not dominated:
            indices.append(i)
    return indices
