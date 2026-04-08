from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.io_utils import load_tasks


def main() -> None:
    main_tasks = load_tasks("tasks/phase3_tasks_v1/*.json")
    external_tasks = load_tasks("tasks/external_eval_v1/*.json")

    if len(main_tasks) != 250:
        raise SystemExit(f"Expected 250 main tasks, found {len(main_tasks)}")
    if len(external_tasks) != 100:
        raise SystemExit(f"Expected 100 external-eval tasks, found {len(external_tasks)}")

    main_by_tool = {}
    for task in main_tasks:
        main_by_tool[task.gold_tool] = main_by_tool.get(task.gold_tool, 0) + 1
        if task.task_set != "main":
            raise SystemExit(f"Main task has wrong task_set: {task.task_id} -> {task.task_set}")
        if not task.template_family:
            raise SystemExit(f"Main task missing template_family: {task.task_id}")
        for variant_name in ("clear", "ambiguous", "incomplete", "misleading"):
            if variant_name not in task.variants:
                raise SystemExit(f"Main task missing variant: {task.task_id} -> {variant_name}")

    external_by_tool = {}
    for task in external_tasks:
        external_by_tool[task.gold_tool] = external_by_tool.get(task.gold_tool, 0) + 1
        if task.task_set != "external_eval":
            raise SystemExit(f"External task has wrong task_set: {task.task_id} -> {task.task_set}")
        if not task.template_family:
            raise SystemExit(f"External task missing template_family: {task.task_id}")
        for variant_name in ("clear", "ambiguous", "incomplete", "misleading"):
            if variant_name not in task.variants:
                raise SystemExit(f"External task missing variant: {task.task_id} -> {variant_name}")

    if sorted(main_by_tool.values()) != [25] * 10:
        raise SystemExit(f"Expected 25 main tasks per tool, found {main_by_tool}")
    if sorted(external_by_tool.values()) != [10] * 10:
        raise SystemExit(f"Expected 10 external tasks per tool, found {external_by_tool}")

    split_df = pd.read_csv(ROOT / "data" / "processed" / "split.csv")
    task_meta_df = pd.read_csv(ROOT / "data" / "processed" / "task_metadata.csv")
    if len(split_df) != 350:
        raise SystemExit(f"Expected 350 split rows, found {len(split_df)}")
    if len(task_meta_df) != 1400:
        raise SystemExit(f"Expected 1400 task metadata rows, found {len(task_meta_df)}")
    if set(split_df["split"]) != {"train", "dev", "test", "external_eval"}:
        raise SystemExit(f"Unexpected split labels: {set(split_df['split'])}")

    print("Phase 3 asset validation passed.")


if __name__ == "__main__":
    main()
