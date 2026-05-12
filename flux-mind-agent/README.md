# Flux Mind Agent

This repository contains the open-source agent side of the Flux Mind project.
ANN model checkpoints and private optimization logic are not included.
The agent delegates ANN inference, optimization, and preference rerank to the private ANN API service.

## Structure

- `app.py`: Flask + Socket.IO entrypoint
- `templates/`: built-in web UI
- `frontend/`: optional Vue frontend project
- `tools/`: modular tool implementation, one tool per folder
- `tools/query_knowledge_base/knowledge/`: RAG metadata placeholder. The local
  FAISS index is not committed.
- `tools/run_optimization/`: runtime API client and tool wrapper for private optimization backend
- `tools/run_optimization/principle_examples/`: review-only illustrative examples of the optimization pipeline, not used at runtime

## Required Environment Variables

- `ANN_API_BASE_URL`
- `ANN_API_KEY`
- `ANN_API_TIMEOUT_SECONDS`
- `ANN_API_BATCH_SIZE`
- `ANN_API_RETRIES`
- `SILICONFLOW_API_KEY`
- `SILICONFLOW_BASE_URL`
- `SILICONFLOW_EMBEDDING_MODEL`

Copy `.env.example` to `.env` and fill in the values before running the app.

## Run

1. Start the private ANN backend first.
2. Then start this agent.

```bash
pip install -r requirements.txt
python app.py
```
