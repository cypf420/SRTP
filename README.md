# SRTP Tool-Calling Failure Analysis

Chinese version: [README_CN.md](./README_CN.md)

This repository contains the Phase 1 and Phase 2 deliverables for the research plan in [engineering_plan_cn.md](./engineering_plan_cn.md).

## Scope Completed

- Phase 1:
  - literature table
  - detailed reading notes
  - research gap statement
  - research boundary statement
- Phase 2:
  - tool schemas
  - task templates with variant-level metadata
  - prompt template
  - batch runner
  - rule-based evaluator
  - validation scripts and evaluator tests

## Layout

- `paper/phase1/`: research positioning materials
- `tools/`: tool schemas
- `tasks/`: task templates
- `prompts/`: prompt templates
- `runner/`: model calling and batch execution
- `evaluator/`: automatic evaluation rules
- `configs/`: model and run configuration templates
- `scripts/`: environment and asset validation utilities
- `tests/`: evaluator tests

## Quick Start

1. Create and activate the recommended conda environment:

```bash
conda env create -f environment.yml
conda activate srtp
```

2. Install dependencies manually only if you are not using conda:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

3. Copy the environment template:

```bash
copy .env.example .env
```

4. Validate the static assets:

```bash
python scripts/validate_assets.py
```

5. Run the environment check:

```bash
python scripts/check_env.py
```

6. Run the evaluator tests:

```bash
python -m pytest tests/test_evaluator.py
```

7. Run a one-sample smoke test after setting model credentials:

```bash
python scripts/smoke_test_tool_call.py --model-config configs/models/openai_gpt4o.yaml
```

8. Run a sample batch:

```bash
python runner/run_batch.py --config configs/runs/sample_run_v1.yaml
```

## Current Assumptions

- The OpenAI backend uses Chat Completions with tool calling.
- The local open model path is left configurable because this machine does not currently expose a local model endpoint.
- No API-backed experiment has been executed yet in this workspace because credentials are not present.
- For this repository, `conda` is the recommended runtime path because most code is Python and several dependencies are easier to keep stable in an isolated environment.
