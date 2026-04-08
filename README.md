# SRTP Tool-Calling Failure Analysis

Chinese version: [README_CN.md](./README_CN.md)

This repository is a research workspace for analyzing tool-calling failures in LLMs.

## Current Status

Completed:

- Phase 1: literature review and research positioning
- Phase 2: tool schemas, base tasks, prompt, runner, evaluator
- Phase 3: expanded task pool, external eval set, split metadata, annotation guideline, processed-data build pipeline

Not completed in this workspace yet:

- API-backed model runs
- merged real `episodes.jsonl`
- real `labels.csv`
- real `run_metadata.csv`
- real `boundary_subset.jsonl`

The blocker is simple: this machine still has no model credentials or local model endpoint.

## What Phase 3 Added

- `tasks/phase3_tasks_v1/`
  - `250` main tasks
- `tasks/external_eval_v1/`
  - `100` held-out external-eval tasks
- `data/annotations/annotation_guideline.md`
- `data/annotations/adjudication.csv`
- `data/processed/split.csv`
- `data/processed/task_metadata.csv`
- `data/processed/data_card.md`
- `scripts/generate_phase3_assets.py`
- `scripts/build_phase3_processed.py`
- `scripts/validate_phase3_assets.py`
- `configs/runs/phase3_*.yaml`

## Layout

- `paper/phase1/`: literature and research-positioning notes
- `tools/`: tool schemas
- `tasks/base_tasks_v1/`: original Phase 2 seed tasks
- `tasks/phase3_tasks_v1/`: expanded main task pool
- `tasks/external_eval_v1/`: held-out external-eval task pool
- `prompts/`: prompt templates
- `runner/`: model calling and batch execution
- `evaluator/`: automatic evaluation rules
- `data/annotations/`: annotation guideline and adjudication template
- `data/processed/`: split metadata, processed outputs, data card
- `scripts/`: validation and data-build utilities
- `configs/runs/`: runnable configs for Phase 2 and Phase 3

## Quick Start

Create and activate the recommended conda environment:

```bash
conda env create -f environment.yml
conda activate srtp
```

Check the environment and Phase 2 assets:

```bash
python scripts/check_env.py
python scripts/validate_assets.py
python -m pytest tests/test_evaluator.py
```

Rebuild and validate Phase 3 assets:

```bash
python scripts/generate_phase3_assets.py
python scripts/build_phase3_processed.py
python scripts/validate_phase3_assets.py
python -m pytest tests/test_phase3_assets.py
```

## Running Real Experiments

After setting model credentials, run:

```bash
python runner/run_batch.py --config configs/runs/phase3_gpt4o_main.yaml
python runner/run_batch.py --config configs/runs/phase3_qwen_main.yaml
python runner/run_batch.py --config configs/runs/phase3_gpt4o_external_eval.yaml
python runner/run_batch.py --config configs/runs/phase3_qwen_external_eval.yaml
python scripts/build_phase3_processed.py
```

This will populate:

- `data/raw_runs/<run_id>/...`
- `data/processed/episodes.jsonl`
- `data/processed/labels.csv`
- `data/processed/run_metadata.csv`
- `data/processed/boundary_subset.jsonl`

## Notes

- `data/processed/split.csv` and `data/processed/task_metadata.csv` are already generated.
- `episodes.jsonl`, `labels.csv`, `run_metadata.csv`, and `boundary_subset.jsonl` are structurally ready but still empty because no real model run has been executed.
- The external eval set is a held-out realistic-style set, not a direct import from a public benchmark.
