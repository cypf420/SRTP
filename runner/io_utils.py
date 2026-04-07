from __future__ import annotations

import glob
import json
from pathlib import Path
from typing import Iterable, List

import yaml

from runner.schemas import ModelConfig, RunConfig, TaskTemplate, ToolSchema


def load_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_yaml(path: str | Path) -> dict:
    return yaml.safe_load(load_text(path))


def load_model_config(path: str | Path) -> ModelConfig:
    return ModelConfig.model_validate(load_yaml(path))


def load_run_config(path: str | Path) -> RunConfig:
    return RunConfig.model_validate(load_yaml(path))


def load_tools(path: str | Path) -> List[ToolSchema]:
    raw = json.loads(load_text(path))
    return [ToolSchema.model_validate(item) for item in raw]


def load_tasks(glob_pattern: str) -> List[TaskTemplate]:
    tasks: List[TaskTemplate] = []
    for path in sorted(glob.glob(glob_pattern)):
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        tasks.extend(TaskTemplate.model_validate(item) for item in raw)
    return tasks


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: str | Path, payload: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
