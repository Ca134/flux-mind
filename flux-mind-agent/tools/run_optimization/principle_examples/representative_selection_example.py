"""Example only: choose representative designs from a Pareto set."""

from __future__ import annotations

import numpy as np


def select_representatives(results: np.ndarray, pareto_indices: list[int]) -> list[dict]:
    pareto = results[pareto_indices]
    total_loss = pareto[:, 14]
    volume = pareto[:, 12]
    footprint = pareto[:, 13]

    return [
        {'label': 'Lowest Loss', 'row': pareto[int(np.argmin(total_loss))]},
        {'label': 'Smallest Volume', 'row': pareto[int(np.argmin(volume))]},
        {'label': 'Compact', 'row': pareto[int(np.argmin(footprint))]},
    ]
