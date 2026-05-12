# ANN API Base

Private ANN inference and optimization service for Flux Mind. The trained model
checkpoint is not included in this public repository.

In the public demo architecture, the ANN model runs on the author's private
server. This directory keeps the API contract, service code, client-facing
schemas, and deployment notes required to run or call a compatible backend. To
use the hosted ANN service or request access to the private checkpoint, contact
the author for permission and usage details.

## Contract

Input row:

`[dc1, dc2, ht, lg1, Nx, Ny, c, f, i]`

Prediction row:

`[L, Pw, Pc]`

## Endpoints

- `GET /health`
- `POST /predict`
- `POST /optimize`
- `POST /rerank`

Authentication for write endpoints uses header `X-API-Key`.

## What `/optimize` Returns

The backend now handles the full private optimization pipeline:

- candidate generation
- parameter filtering
- ANN inference
- derived metrics (`V`, `S`, `P`)
- Pareto front extraction
- representative design selection
- result caching for later rerank

So the server returns ready-to-use feasible designs directly, not just raw ANN predictions.

## Start

1. Create a virtual environment.
2. Install `requirements.txt`.
3. Copy `.env.example` to `.env` and set `ANN_API_KEY`.
4. Confirm `ANN_MODEL_PATH` points to your local checkpoint.
5. Run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Mock Mode

Set:

```env
ANN_RUNTIME_MODE=mock
ANN_ALLOW_MOCK_MODEL=true
```

This lets you verify API wiring before loading the real checkpoint.
