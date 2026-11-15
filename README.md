# SRTP Tool-Calling Failure Analysis

The midterm submission includes the [report PDF](paper/midterm_report_cn.pdf), [Markdown report](paper/midterm_report_cn.md), and [experiment evidence](paper/midterm_results/README.md). Cross-model replication is pending.

Chinese version: [README_CN.md](./README_CN.md)

This repository is a research workspace for analyzing tool-calling failures in LLMs.

## Current Status

Completed:

- Phase 1: literature review and research positioning
- Phase 2: tool schemas, base tasks, prompt, runner, evaluator
- Phase 3: expanded task pool, external eval set, split metadata, annotation guideline, processed-data build pipeline

- GLM-4.7 and Qwen2.5-7B ran the same 1,000 main inputs. The merged data, automatic labels, and Qwen inputs for representation analysis are available.
- The [midterm report in Chinese](paper/midterm_report_cn.md) covers the revised evaluation, pre-call feature baseline and two paired Qwen interventions.

Human adjudication, held-out runs, GLM replication of the interventions and the defense prototype are pending.

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
python runner/run_batch.py --config configs/runs/phase3_glm_main.yaml
python runner/run_batch.py --config configs/runs/phase3_qwen_main.yaml
python runner/run_batch.py --config configs/runs/phase3_glm_external_eval.yaml
python runner/run_batch.py --config configs/runs/phase3_qwen_external_eval.yaml
python scripts/build_phase3_processed.py
```

This will populate:

- `data/raw_runs/<run_id>/...`
- `data/processed/episodes.jsonl`
- `data/processed/labels.csv`
- `data/processed/run_metadata.csv`
- `data/processed/boundary_subset.jsonl`

## Interrupt And Resume

The batch runner now writes one episode at a time.

If a run is interrupted, restart it with the same `run_id`:

```bash
python runner/run_batch.py --config configs/runs/phase3_glm_main.yaml --run-id <existing_run_id> --resume
```

Resume mode skips `sample_id`s that already exist in `episodes.jsonl`.

## Notes

- `data/processed/split.csv` and `data/processed/task_metadata.csv` are already generated.
- `episodes.jsonl`, `labels.csv`, `run_metadata.csv`, and `boundary_subset.jsonl` contain 2,000 main episodes, 2,000 automatic labels, 2 run records, and 1,000 Qwen inputs for representation analysis, respectively.
- The external eval set is a held-out realistic-style set, not a direct import from a public benchmark.
- The recommended model pair is `GLM-4.7 + Qwen2.5-7B-Instruct`.
