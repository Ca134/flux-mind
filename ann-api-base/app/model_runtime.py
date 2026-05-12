from __future__ import annotations

import os
import threading
from math import ceil
from typing import Optional

import numpy as np
import torch
from torch import nn

from .config import settings


class Net(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.shared_layers = nn.Sequential(
            nn.Linear(9, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
        )
        self.branch_L = nn.Sequential(nn.Linear(32, 8), nn.ReLU(), nn.Linear(8, 1))
        self.branch_Pw = nn.Sequential(
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
        )
        self.branch_Pc = nn.Sequential(
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        shared_features = self.shared_layers(x)
        L = self.branch_L(shared_features)
        Pw = self.branch_Pw(shared_features)
        Pc = self.branch_Pc(shared_features)
        return torch.cat([L, Pw, Pc], dim=1)


class ModelRuntime:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._net: Optional[Net] = None
        self._input_scaler = None
        self._output_scalers = None
        if settings.device == 'cuda' and torch.cuda.is_available():
            self._device = torch.device('cuda')
        else:
            self._device = torch.device('cpu')

    @property
    def is_loaded(self) -> bool:
        return self._net is not None or settings.runtime_mode == 'mock'

    def _load_checkpoint(self) -> None:
        if self._net is not None:
            return
        if not settings.model_path:
            raise RuntimeError('ANN_MODEL_PATH is not configured')
        if not os.path.exists(settings.model_path):
            raise RuntimeError('ANN model checkpoint file was not found')

        print(f"[ANN API] Loading checkpoint from {settings.model_path}", flush=True)
        checkpoint = torch.load(settings.model_path, map_location=self._device, weights_only=False)
        net = Net().to(self._device)
        net.load_state_dict(checkpoint['model_state'])
        net.eval()

        self._net = net
        self._input_scaler = checkpoint['input_scaler']
        self._output_scalers = checkpoint['output_scalers']
        print("[ANN API] Checkpoint loaded successfully", flush=True)

    def ensure_loaded(self) -> None:
        if settings.runtime_mode == 'mock':
            if not settings.allow_mock_model:
                raise RuntimeError('Mock runtime is disabled. Set ANN_ALLOW_MOCK_MODEL=true to enable it.')
            return
        if self._net is not None:
            return
        with self._lock:
            if self._net is None:
                self._load_checkpoint()

    def predict(self, x_input: np.ndarray, batch_size: Optional[int] = None) -> np.ndarray:
        self.ensure_loaded()
        x_input = np.asarray(x_input, dtype=np.float32)
        if x_input.ndim != 2 or x_input.shape[1] != 9:
            raise ValueError('Expected x_input with shape (N, 9)')

        if settings.runtime_mode == 'mock':
            return self._predict_mock(x_input)
        return self._predict_checkpoint(x_input, batch_size or settings.default_batch_size)

    def _predict_checkpoint(self, x_input: np.ndarray, batch_size: int) -> np.ndarray:
        assert self._net is not None
        y_pred_list = []
        total_batches = max(1, ceil(len(x_input) / batch_size))

        for batch_index, start in enumerate(range(0, len(x_input), batch_size), start=1):
            x_batch = x_input[start : start + batch_size]
            print(
                f"[ANN API] Inference batch {batch_index}/{total_batches} "
                f"(size={len(x_batch)})",
                flush=True,
            )
            x_reorder = np.stack(
                [
                    x_batch[:, 6],
                    x_batch[:, 0],
                    x_batch[:, 1],
                    x_batch[:, 7],
                    x_batch[:, 2],
                    x_batch[:, 8],
                    x_batch[:, 3],
                    x_batch[:, 4],
                    x_batch[:, 5],
                ],
                axis=1,
            )
            x_log = np.log10(x_reorder.astype(np.float32))
            x_scaled = self._input_scaler.transform(x_log)
            x_tensor = torch.from_numpy(x_scaled).float().to(self._device)

            with torch.no_grad():
                y_scaled = self._net(x_tensor).cpu().numpy()

            y_physical = np.zeros_like(y_scaled)
            for column_index in range(3):
                y_log = self._output_scalers[column_index].inverse_transform(
                    y_scaled[:, column_index].reshape(-1, 1)
                ).flatten()
                y_physical[:, column_index] = 10 ** y_log

            y_pred_list.append(y_physical)
            print(
                f"[ANN API] Finished inference batch {batch_index}/{total_batches}",
                flush=True,
            )

        return np.vstack(y_pred_list)

    def _predict_mock(self, x_input: np.ndarray) -> np.ndarray:
        dc1 = x_input[:, 0]
        dc2 = x_input[:, 1]
        ht = x_input[:, 2]
        lg1 = x_input[:, 3]
        Nx = x_input[:, 4]
        Ny = x_input[:, 5]
        c = x_input[:, 6]
        f = x_input[:, 7]
        current = x_input[:, 8]

        turns = np.maximum(Nx * Ny, 1.0)
        inductance = (turns * turns) / np.maximum(lg1 + 0.1, 0.1)
        inductance = 0.02 * inductance + 0.15 * ht + 0.05 * dc1

        copper_loss = 0.00012 * turns * current * current + 0.00002 * f * c
        core_loss = 0.00001 * f * (dc1 + dc2 + ht) + 0.0003 * current

        return np.column_stack([inductance, copper_loss, core_loss]).astype(np.float32)


runtime = ModelRuntime()
