# FluxMind Benchmark Data

This folder keeps the benchmark data in a simple form:

- `raw_runs/llm_only/`: original LLM-only run records, including interaction logs.
- `raw_runs/fluxmind/`: original FluxMind offline scripted run records, including interaction/tool logs.
- `validated_results/llm_only/`: original ANN/Maxwell validation summaries for LLM-only outputs.
- `task_summary.csv`: a small per-task summary and target-hit statistics.
- `representative_cases.csv`: A2, A4, and B3 values used in the paper's representative comparison table.
- `metadata.json`: source and generation metadata.

The raw run files are copied from `changed_base_on_model/paper/myself_final/coverage_exp` without rewriting their internal records. Temporary `.tmp.json` files are excluded.

Summary: FluxMind hits the target inductance range in 12/12 tasks, while the LLM-only baseline hits it in 5/12 tasks.

Units follow the column names: kHz, A, uH, W, and mm^3.
