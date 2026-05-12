from __future__ import annotations

import os
import time
from dataclasses import dataclass
from math import ceil
from typing import Optional

import numpy as np
import requests


@dataclass(frozen=True)
class ClientSettings:
    base_url: str = os.getenv('ANN_API_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
    api_key: str = os.getenv('ANN_API_KEY', '')
    timeout_seconds: int = int(os.getenv('ANN_API_TIMEOUT_SECONDS', '60'))
    default_batch_size: int = int(os.getenv('ANN_API_BATCH_SIZE', '5000'))
    retries: int = int(os.getenv('ANN_API_RETRIES', '1'))


class AnnApiClient:
    def __init__(self, settings: Optional[ClientSettings] = None) -> None:
        self.settings = settings or ClientSettings()
        if not self.settings.api_key:
            raise ValueError('ANN_API_KEY is not configured')

    def _headers(self) -> dict[str, str]:
        return {
            'X-API-Key': self.settings.api_key,
            'Content-Type': 'application/json',
        }

    def health(self) -> dict:
        response = requests.get(
            f'{self.settings.base_url}/health',
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def predict(self, x_input: np.ndarray, batch_size: Optional[int] = None, request_id: Optional[str] = None) -> np.ndarray:
        x_input = np.asarray(x_input, dtype=np.float32)
        if x_input.ndim != 2 or x_input.shape[1] != 9:
            raise ValueError('Expected x_input with shape (N, 9)')

        effective_batch_size = int(batch_size or self.settings.default_batch_size)
        total_rows = len(x_input)
        total_batches = max(1, ceil(total_rows / effective_batch_size))
        prediction_batches: list[np.ndarray] = []
        max_attempts = max(self.settings.retries, 0) + 1

        for batch_index, start in enumerate(range(0, total_rows, effective_batch_size), start=1):
            stop = min(start + effective_batch_size, total_rows)
            x_batch = x_input[start:stop]
            payload = {
                'inputs': x_batch.tolist(),
                'batch_size': effective_batch_size,
                'request_id': request_id,
            }
            print(
                f'[ANN API client] Sending batch {batch_index}/{total_batches} with rows {start}:{stop} (size={len(x_batch)})',
                flush=True,
            )

            last_error: Optional[Exception] = None
            for attempt in range(max_attempts):
                try:
                    response = requests.post(
                        f'{self.settings.base_url}/predict',
                        json=payload,
                        headers=self._headers(),
                        timeout=self.settings.timeout_seconds,
                    )
                    response.raise_for_status()
                    body = response.json()
                    predictions = np.asarray(body['predictions'], dtype=np.float32)
                    if predictions.shape != (len(x_batch), 3):
                        raise RuntimeError('ANN API returned an unexpected prediction shape')
                    prediction_batches.append(predictions)
                    print(f'[ANN API client] Completed batch {batch_index}/{total_batches}', flush=True)
                    break
                except requests.RequestException as exc:
                    last_error = exc
                    if attempt + 1 >= max_attempts:
                        raise RuntimeError(f'ANN API request failed: {last_error}') from last_error
                    time.sleep(0.5 * (attempt + 1))

        return np.vstack(prediction_batches)

    def optimize(self, user_params: dict, batch_size: Optional[int] = None) -> dict:
        payload = {
            'user_params': user_params,
            'batch_size': batch_size or self.settings.default_batch_size,
        }
        response = requests.post(
            f'{self.settings.base_url}/optimize',
            json=payload,
            headers=self._headers(),
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def rerank(self, result_id: str, preference: str = 'default', strength: str = 'medium', top_n: int = 10) -> dict:
        payload = {
            'result_id': result_id,
            'preference': preference,
            'strength': strength,
            'top_n': top_n,
        }
        response = requests.post(
            f'{self.settings.base_url}/rerank',
            json=payload,
            headers=self._headers(),
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


def optimize_via_api(user_params: dict, batch_size: Optional[int] = None) -> dict:
    client = AnnApiClient()
    return client.optimize(user_params=user_params, batch_size=batch_size)


def rerank_via_api(result_id: str, preference: str = 'default', strength: str = 'medium', top_n: int = 10) -> dict:
    client = AnnApiClient()
    return client.rerank(result_id=result_id, preference=preference, strength=strength, top_n=top_n)
