from pathlib import Path

import pandas as pd

from runner.io_utils import load_tasks
from scripts.build_phase3_processed import build_boundary_subset


ROOT = Path(__file__).resolve().parents[1]


def test_phase3_task_pool_sizes() -> None:
    main_tasks = load_tasks(str(ROOT / "tasks" / "phase3_tasks_v1" / "*.json"))
    external_tasks = load_tasks(str(ROOT / "tasks" / "external_eval_v1" / "*.json"))

    assert len(main_tasks) == 250
    assert len(external_tasks) == 100
    assert {task.task_set for task in main_tasks} == {"main"}
    assert {task.task_set for task in external_tasks} == {"external_eval"}


def test_phase3_processed_metadata_sizes() -> None:
    split_df = pd.read_csv(ROOT / "data" / "processed" / "split.csv")
    meta_df = pd.read_csv(ROOT / "data" / "processed" / "task_metadata.csv")

    assert len(split_df) == 350
    assert len(meta_df) == 1400
    assert set(split_df["split"]) == {"train", "dev", "test", "external_eval"}


def test_boundary_subset_keeps_labels_from_the_same_run() -> None:
    qwen = {
        "run_id": "qwen_run",
        "sample_id": "task_001__clear",
        "task_id": "task_001",
        "model_name": "qwen2.5:7b",
        "split": "train",
        "task_set": "main",
        "variant_name": "clear",
    }
    glm = {**qwen, "run_id": "glm_run", "model_name": "glm-4.7"}
    labels = [{**qwen, "main_label": "param_error"}, {**glm, "main_label": "correct"}]

    for ordered_labels in (labels, list(reversed(labels))):
        subset = build_boundary_subset([qwen, glm], ordered_labels)
        assert [(row["run_id"], row["main_label"]) for row in subset] == [("qwen_run", "param_error")]
