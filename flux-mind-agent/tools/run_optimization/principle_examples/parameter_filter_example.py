"""Example only: illustrate scalar/range filtering over candidate rows."""

from __future__ import annotations

import numpy as np

COLUMN_MAP = {
    'dc1': 0,
    'dc2': 1,
    'ht': 2,
    'lg1': 3,
    'Nx': 4,
    'Ny': 5,
    'c': 6,
    'f': 7,
    'i': 8,
}


def filter_by_user_params(candidates: np.ndarray, user_params: dict) -> np.ndarray:
    mask = np.ones(len(candidates), dtype=bool)
    for name, value in user_params.items():
        if name not in COLUMN_MAP:
            continue
        column = COLUMN_MAP[name]
        if isinstance(value, dict):
            if 'min' in value:
                mask &= candidates[:, column] >= float(value['min'])
            if 'max' in value:
                mask &= candidates[:, column] <= float(value['max'])
        else:
            mask &= np.isclose(candidates[:, column], float(value), rtol=0.01)
    return candidates[mask]
