# FluxMind

FluxMind is a prototype AI assistant for power-electronics design. It turns a
natural-language design request into structured parameters, calls a private ANN
optimization backend, and returns candidate magnetic-component designs with
loss, volume, and trade-off information.

The public repository contains the main application code:

- `flux-mind-agent/`: the LLM agent, tool orchestration layer, web UI, and API
  client for the optimization backend.
- `ann-api-base/`: the FastAPI backend interface for ANN prediction,
  optimization, and reranking.

## What It Does

A user can describe a task such as:

```text
Design a Buck converter inductor at 200 kHz and 10 A.
The target inductance is 5-10 uH, and low loss is more important than volume.
```

FluxMind then:

1. Extracts the known design requirements.
2. Tracks missing parameters and asks follow-up questions when needed.
3. Sends a structured request to the ANN optimization service.
4. Receives candidate designs from the backend.
5. Explains the recommended designs and their loss-volume trade-offs.

## ANN Model Notice

The trained ANN model is not open-sourced in this repository.

I run the ANN model on my own private server. This repository keeps the public
application code, API contract, and integration path so that the agent can call a
compatible ANN service.

If you want to use the hosted ANN service or request access to the private model,
please contact the author for permission and usage details.

For local development without the private checkpoint, you can run the backend in
mock mode.

## Repository Structure

```text
flux_mind/
├── ann-api-base/
│   ├── app/
│   ├── models/README.md
│   ├── .env.example
│   └── requirements.txt
├── flux-mind-agent/
│   ├── app.py
│   ├── core/
│   ├── tools/
│   ├── templates/
│   ├── frontend/
│   ├── .env.example
│   └── requirements.txt
├── LICENSE
└── README.md
```

## Quick Start

FluxMind has two services:

1. `ann-api-base`: ANN prediction and optimization API.
2. `flux-mind-agent`: LLM agent and web interface.

Start the ANN backend first, then start the agent.

### 1. Start ANN API Backend

```bash
cd ann-api-base
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```env
ANN_API_HOST=0.0.0.0
ANN_API_PORT=8000
ANN_API_KEY=replace_me
ANN_MODEL_PATH=/path/to/private_checkpoint.pth
ANN_DEVICE=cpu
ANN_RUNTIME_MODE=checkpoint
ANN_MAX_POINTS=50000
ANN_DEFAULT_BATCH_SIZE=5000
ANN_OPTIMIZATION_CACHE_SIZE=3
ANN_ALLOW_MOCK_MODEL=false
```

Run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

To test the API wiring without the private model:

```env
ANN_RUNTIME_MODE=mock
ANN_ALLOW_MOCK_MODEL=true
```

### 2. Start FluxMind Agent

```bash
cd ../flux-mind-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```env
ANN_API_BASE_URL=http://127.0.0.1:8000
ANN_API_KEY=replace_me
ANN_API_TIMEOUT_SECONDS=60
ANN_API_BATCH_SIZE=5000
ANN_API_RETRIES=1

SILICONFLOW_API_KEY=replace_me
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-8B
```

Run:

```bash
python app.py
```

Open the local web page shown in the Flask output.

## Main API Endpoints

The ANN backend exposes:

- `GET /health`: backend and model health check.
- `POST /predict`: direct ANN prediction.
- `POST /optimize`: candidate generation, ANN evaluation, Pareto filtering, and
  representative design selection.
- `POST /rerank`: rerank cached optimization results by user preference.

Authenticated endpoints use the `X-API-Key` header.

## License

FluxMind is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for
details.
