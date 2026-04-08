from pathlib import Path

import pandas as pd

from runner.io_utils import load_tasks


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
