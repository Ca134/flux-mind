"""Example only: illustrate how a discrete candidate set can be built."""

from __future__ import annotations

import numpy as np


def generate_candidate_points() -> np.ndarray:
    dc1_values = np.array([8.0, 10.0], dtype=np.float32)
    nx_values = np.array([4, 6], dtype=np.float32)
    ny_values = np.array([3, 5], dtype=np.float32)
    c_values = np.array([1.0, 1.5], dtype=np.float32)
    f_values = np.array([100.0, 200.0], dtype=np.float32)
    i_values = np.array([5.0, 10.0], dtype=np.float32)

    rows = []
    for dc1 in dc1_values:
        for nx in nx_values:
            for ny in ny_values:
                for c in c_values:
                    if nx * c >= 10 or ny * c >= 10:
                        continue
                    for f in f_values:
                        for current in i_values:
                            rows.append([dc1, 3.0, 6.0, 0.5, nx, ny, c, f, current])
    return np.asarray(rows, dtype=np.float32)
