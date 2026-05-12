"""Example only: stand-in for private ANN inference.

The real project now calls the private ANN backend instead of doing model inference here.
"""

from __future__ import annotations

import numpy as np


class DemoAnnModel:
    def predict(self, x_input: np.ndarray) -> np.ndarray:
        turns = np.maximum(x_input[:, 4] * x_input[:, 5], 1.0)
        inductance = 0.05 * turns + 0.01 * x_input[:, 2]
        copper_loss = 0.002 * x_input[:, 8] * turns
        core_loss = 0.0005 * x_input[:, 7] * x_input[:, 0]
        return np.column_stack([inductance, copper_loss, core_loss]).astype(np.float32)
