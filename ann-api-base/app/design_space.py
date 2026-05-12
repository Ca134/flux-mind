from __future__ import annotations

import math
from typing import Iterable

import numpy as np

BMAX = 0.3
MU = 4 * math.pi * 1e-7

DC1_RANGE = np.arange(5, 31, 1, dtype=np.float32)
DC2_RANGE = np.arange(1, 11, 1, dtype=np.float32)
HT_RANGE = np.arange(1, 11, 1, dtype=np.float32)
LG1_RANGE = np.arange(0.1, 4.1, 0.5, dtype=np.float32)
NX_RANGE = np.arange(1, 11, 1, dtype=np.float32)
NY_RANGE = np.arange(1, 11, 1, dtype=np.float32)
C_RANGE = np.arange(1, 5.5, 0.5, dtype=np.float32)
F_RANGE = np.arange(100, 501, 100, dtype=np.float32)
I_VALS_POOL = np.array([5, 10, 20, 30, 50], dtype=np.float32)

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

_design_space_cache: dict[tuple[tuple[float, ...], tuple[float, ...]], np.ndarray] = {}


def _resolve_operating_values(value: object, default_grid: Iterable[float]) -> np.ndarray:
    grid = np.asarray(list(default_grid), dtype=np.float32)
    if value is None:
        return grid

    if isinstance(value, dict):
        mask = np.ones(len(grid), dtype=bool)
        if 'min' in value:
            mask &= grid >= float(value['min'])
        if 'max' in value:
            mask &= grid <= float(value['max'])
        return grid[mask]

    return np.asarray([float(value)], dtype=np.float32)


def generate_all_valid_samples(
    f_values: np.ndarray | None = None,
    i_values: np.ndarray | None = None,
) -> np.ndarray:
    freq_values = np.asarray(F_RANGE if f_values is None else f_values, dtype=np.float32)
    current_values = np.asarray(I_VALS_POOL if i_values is None else i_values, dtype=np.float32)

    valid_batches: list[np.ndarray] = []
    total_count = 0

    for dc1 in DC1_RANGE:
        for nx in NX_RANGE:
            for ny in NY_RANGE:
                for c in C_RANGE:
                    if not (0.1 < nx * c < 10 and 0.1 < ny * c < 10):
                        continue

                    dc2_mesh, ht_mesh, lg1_mesh = np.meshgrid(DC2_RANGE, HT_RANGE, LG1_RANGE, indexing='ij')
                    dc2_flat = dc2_mesh.ravel()
                    ht_flat = ht_mesh.ravel()
                    lg1_flat = lg1_mesh.ravel()

                    i_max = (BMAX * lg1_flat * 0.001) / (MU * nx * ny)
                    valid_i_mask = (current_values[:, None] <= i_max) & (current_values[:, None] >= 1)
                    valid_geo_mask = np.any(valid_i_mask, axis=0)
                    if not np.any(valid_geo_mask):
                        continue

                    geo_indices = np.where(valid_geo_mask)[0]
                    local_i_indices, local_geo_indices = np.where(valid_i_mask[:, geo_indices])
                    actual_geo_indices = geo_indices[local_geo_indices]
                    if len(actual_geo_indices) == 0:
                        continue

                    n_geometry_rows = len(actual_geo_indices)
                    geometry_block = np.column_stack(
                        [
                            np.full(n_geometry_rows, dc1, dtype=np.float32),
                            dc2_flat[actual_geo_indices],
                            ht_flat[actual_geo_indices],
                            lg1_flat[actual_geo_indices],
                            np.full(n_geometry_rows, nx, dtype=np.float32),
                            np.full(n_geometry_rows, ny, dtype=np.float32),
                            np.full(n_geometry_rows, c, dtype=np.float32),
                        ]
                    ).astype(np.float32)

                    for f in freq_values:
                        batch = np.column_stack(
                            [
                                geometry_block,
                                np.full(n_geometry_rows, f, dtype=np.float32),
                                current_values[local_i_indices],
                            ]
                        ).astype(np.float32)
                        valid_batches.append(batch)
                        total_count += len(batch)

    result = np.vstack(valid_batches) if valid_batches else np.empty((0, 9), dtype=np.float32)
    print(f'[ANN API] Generated design space with {total_count} valid combinations', flush=True)
    return np.round(result, 2)


def get_design_space(user_params: dict) -> np.ndarray:
    f_values = _resolve_operating_values(user_params.get('f'), F_RANGE)
    i_values = _resolve_operating_values(user_params.get('i'), I_VALS_POOL)
    cache_key = (
        tuple(np.round(f_values.astype(np.float64), 6).tolist()),
        tuple(np.round(i_values.astype(np.float64), 6).tolist()),
    )
    if cache_key not in _design_space_cache:
        print(f'[ANN API] Building design space for f={list(f_values)} i={list(i_values)}', flush=True)
        _design_space_cache[cache_key] = generate_all_valid_samples(f_values=f_values, i_values=i_values)
    return _design_space_cache[cache_key]


def filter_by_user_params(design_space: np.ndarray, user_params: dict) -> np.ndarray:
    mask = np.ones(len(design_space), dtype=bool)
    for param, value in user_params.items():
        if param not in COLUMN_MAP:
            continue
        column_index = COLUMN_MAP[param]
        if isinstance(value, dict):
            if 'min' in value:
                mask &= design_space[:, column_index] >= float(value['min'])
            if 'max' in value:
                mask &= design_space[:, column_index] <= float(value['max'])
        else:
            mask &= np.isclose(design_space[:, column_index], float(value), rtol=0.01)
    return design_space[mask]
