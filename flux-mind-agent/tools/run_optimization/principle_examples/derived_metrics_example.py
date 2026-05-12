"""Example only: derive volume, footprint and total loss from inputs and ANN outputs."""

from __future__ import annotations

import numpy as np


def compute_derived_values(x_values: np.ndarray, y_values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    dc1, dc2, ht = x_values[:, 0], x_values[:, 1], x_values[:, 2]
    nx, ny, c = x_values[:, 4], x_values[:, 5], x_values[:, 6]
    pw, pc = y_values[:, 1], y_values[:, 2]

    width = dc1 + 2 * dc2 + 2 * nx * c + 2.8
    length = dc1 + 2 * nx * c + 1.4
    height = 2 * ht + ny * c + 1.4

    volume = width * length * height
    footprint = width * length
    total_loss = pw + pc
    return volume.astype(np.float32), footprint.astype(np.float32), total_loss.astype(np.float32)
