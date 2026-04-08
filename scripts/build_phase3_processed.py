from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluator.rules import evaluate_prediction
from runner.io_utils import load_tasks, load_tools
from runner.schemas import TaskTemplate

PROCESSED_DIR = ROOT / "data" / "processed"
MAIN_GLOB = str(ROOT / "tasks" / "phase3_tasks_v1" / "*.json")
EXTERNAL_GLOB = str(ROOT / "tasks" / "external_eval_v1" / "*.json")
RAW_RUN_GLOB = str(ROOT / "data" / "raw_runs" / "*" / "episodes.jsonl")
MANIFEST_GLOB = str(ROOT / "data" / "raw_runs" / "*" / "run_manifest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 3 processed metadata and merge raw runs when available.")
    parser.add_argument("--tools", default=str(ROOT / "tools" / "tool_schemas_v1.json"), help="Path to tool schema JSON.")
    return parser.parse_args()


def stable_family_order(family: str) -> str:
    return hashlib.md5(family.encode("utf-8")).hexdigest()


def assign_split(tasks: List[TaskTemplate]) -> Dict[str, str]:
    families = sorted({task.template_family or task.task_id for task in tasks}, key=stable_family_order)
    train_cutoff = 30
    dev_cutoff = 40
    mapping: Dict[str, str] = {}
    for idx, family in enumerate(families):
        if idx < train_cutoff:
            mapping[family] = "train"
        elif idx < dev_cutoff:
            mapping[family] = "dev"
        else:
            mapping[family] = "test"
    return mapping


def task_rows(tasks: List[TaskTemplate], split_map: Dict[str, str], task_set: str) -> tuple[List[dict], List[dict]]:
    task_level_rows: List[dict] = []
    sample_level_rows: List[dict] = []
    for task in tasks:
        family = task.template_family or task.task_id
        split = "external_eval" if task_set == "external_eval" else split_map[family]
        task_level_rows.append(
            {
                "task_id": task.task_id,
                "template_family": family,
                "task_set": task.task_set,
                "split": split,
                "language": task.language,
                "domain": task.domain,
                "gold_tool": task.gold_tool,
                "intent": task.intent,
            }
        )
        for variant_name, variant in task.variants.items():
            sample_level_rows.append(
                {
                    "sample_id": f"{task.task_id}__{variant_name}",
                    "task_id": task.task_id,
                    "template_family": family,
                    "task_set": task.task_set,
                    "split": split,
                    "variant_name": variant_name,
                    "language": task.language,
                    "domain": task.domain,
                    "gold_tool": task.gold_tool,
                    "intent": task.intent,
                    "need_clarification": variant.need_clarification,
                    "clarification_fields": json.dumps(variant.clarification_fields, ensure_ascii=False),
                    "distractor_tools": json.dumps(task.distractor_tools, ensure_ascii=False),
                    "gold_params": json.dumps(task.gold_params, ensure_ascii=False),
                }
            )
    return task_level_rows, sample_level_rows


def write_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def collect_raw_runs(tasks_by_id: Dict[str, TaskTemplate], split_by_task: Dict[str, str], tool_registry: Dict[str, Any]) -> tuple[List[dict], List[dict], List[dict]]:
    episodes: List[dict] = []
    labels: List[dict] = []
    run_rows: List[dict] = []

    manifests = {Path(path).parent.name: json.loads(Path(path).read_text(encoding="utf-8")) for path in glob.glob(MANIFEST_GLOB)}
    for run_id, manifest in manifests.items():
        tasks_glob = manifest.get("tasks_glob", "") or ""
        if "phase3_tasks_v1" not in tasks_glob and "external_eval_v1" not in tasks_glob:
            continue
        run_rows.append(
            {
                "run_id": manifest.get("run_id", run_id),
                "run_name": manifest.get("run_name"),
                "model_name": manifest.get("model_name"),
                "started_at": manifest.get("started_at"),
                "finished_at": manifest.get("finished_at"),
                "task_count": manifest.get("task_count"),
                "episode_count": manifest.get("episode_count"),
                "prompt_version": manifest.get("prompt_version"),
                "tools_path": manifest.get("tools_path"),
                "tasks_glob": tasks_glob,
            }
        )

    for path in glob.glob(RAW_RUN_GLOB):
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                episode = json.loads(line)
                task_id = episode["task_id"]
                if task_id not in tasks_by_id:
                    continue
                task = tasks_by_id[task_id]
                split = split_by_task[task_id]
                enriched = {
                    **episode,
                    "task_set": task.task_set,
                    "split": split,
                    "language": task.language,
                    "domain": task.domain,
                }
                episodes.append(enriched)
                prediction = episode["prediction"]
                result = evaluate_prediction(
                    sample_id=episode["sample_id"],
                    task=task,
                    variant_name=episode["variant_name"],
                    predicted_tool=prediction.get("tool_name_pred"),
                    predicted_args=prediction.get("arguments_pred", {}),
                    tool_registry=tool_registry,
                )
                labels.append(
                    {
                        "run_id": episode["run_id"],
                        "sample_id": episode["sample_id"],
                        "task_id": task_id,
                        "variant_name": episode["variant_name"],
                        "split": split,
                        "task_set": task.task_set,
                        "model_name": episode["model_name"],
                        "main_label": result.main_label,
                        "sublabels": json.dumps(result.sublabels, ensure_ascii=False),
                        "correct_tool": result.correct_tool,
                        "correct_params": result.correct_params,
                        "notes": json.dumps(result.notes, ensure_ascii=False),
                    }
                )
    return episodes, labels, run_rows


def build_boundary_subset(episodes: List[dict], labels: List[dict]) -> List[dict]:
    label_map = {row["sample_id"]: row for row in labels}
    rows: List[dict] = []
    open_model_tokens = ("qwen", "llama", "mistral", "phi", "gemma")
    for episode in episodes:
        model_name = (episode.get("model_name") or "").lower()
        if not any(token in model_name for token in open_model_tokens):
            continue
        user_message = ""
        for message in reversed(episode.get("messages", [])):
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break
        label_row = label_map.get(episode["sample_id"])
        rows.append(
            {
                "sample_id": episode["sample_id"],
                "task_id": episode["task_id"],
                "run_id": episode["run_id"],
                "model_name": episode["model_name"],
                "split": episode["split"],
                "task_set": episode["task_set"],
                "variant_name": episode["variant_name"],
                "main_label": label_row["main_label"] if label_row else None,
                "text": user_message,
            }
        )
    return rows


def ensure_empty_csv(path: Path, columns: List[str]) -> None:
    pd.DataFrame(columns=columns).to_csv(path, index=False)


def main() -> None:
    args = parse_args()
    main_tasks = load_tasks(MAIN_GLOB)
    external_tasks = load_tasks(EXTERNAL_GLOB)
    split_map = assign_split(main_tasks)

    task_level_rows, sample_rows = task_rows(main_tasks, split_map, "main")
    external_task_rows, external_sample_rows = task_rows(external_tasks, split_map, "external_eval")
    task_level_rows.extend(external_task_rows)
    sample_rows.extend(external_sample_rows)

    tasks_by_id = {task.task_id: task for task in main_tasks + external_tasks}
    split_by_task = {row["task_id"]: row["split"] for row in task_level_rows}

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(task_level_rows).sort_values(["task_set", "task_id"]).to_csv(PROCESSED_DIR / "split.csv", index=False)
    pd.DataFrame(sample_rows).sort_values(["task_set", "task_id", "variant_name"]).to_csv(PROCESSED_DIR / "task_metadata.csv", index=False)

    tool_registry = {tool.name: tool for tool in load_tools(args.tools)}
    episodes, labels, run_rows = collect_raw_runs(tasks_by_id, split_by_task, tool_registry)
    write_jsonl(PROCESSED_DIR / "episodes.jsonl", episodes)
    boundary_rows = build_boundary_subset(episodes, labels)
    write_jsonl(PROCESSED_DIR / "boundary_subset.jsonl", boundary_rows)

    if labels:
        pd.DataFrame(labels).to_csv(PROCESSED_DIR / "labels.csv", index=False)
    else:
        ensure_empty_csv(PROCESSED_DIR / "labels.csv", ["run_id", "sample_id", "task_id", "variant_name", "split", "task_set", "model_name", "main_label", "sublabels", "correct_tool", "correct_params", "notes"])

    if run_rows:
        pd.DataFrame(run_rows).to_csv(PROCESSED_DIR / "run_metadata.csv", index=False)
    else:
        ensure_empty_csv(PROCESSED_DIR / "run_metadata.csv", ["run_id", "run_name", "model_name", "started_at", "finished_at", "task_count", "episode_count", "prompt_version", "tools_path", "tasks_glob"])

    print(f"Main tasks: {len(main_tasks)}")
    print(f"External eval tasks: {len(external_tasks)}")
    print(f"Sample metadata rows: {len(sample_rows)}")
    print(f"Merged episodes: {len(episodes)}")
    print(f"Boundary subset rows: {len(boundary_rows)}")


if __name__ == "__main__":
    main()
