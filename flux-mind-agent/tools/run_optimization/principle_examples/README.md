# Run Optimization Principle Examples

This folder is for open-source review only.

It shows the private optimization pipeline as small, readable examples, but these files are not imported by the running agent.
The real execution path in the public repo is still:

- `tools/run_optimization/handler.py`
- `tools/run_optimization/service.py`
- `tools/run_optimization/ann_api_client.py`

The example files here correspond to the conceptual stages that now run in the private ANN backend:

- candidate generation
- user-parameter filtering
- ANN inference stub
- derived metric calculation (`V`, `S`, `P`)
- Pareto filtering
- representative design selection
- preference rerank
