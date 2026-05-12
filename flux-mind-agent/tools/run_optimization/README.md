# run_optimization Tool

Runtime path:

- `handler.py`: tool entry used by the agent
- `service.py`: trigger checks and backend call wrapper
- `ann_api_client.py`: HTTP client for private ANN backend
- `schema.py`: tool schema exposed to the model

Review-only path:

- `principle_examples/`: small example code for candidate generation, filtering, ANN stub inference, derived metrics, Pareto selection, representative selection, and preference rerank

The files in `principle_examples/` are not imported by the running agent. They are included only to show the algorithmic idea in the open-source repository.
