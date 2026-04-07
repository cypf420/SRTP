from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluator.rules import evaluate_prediction
from runner.io_utils import load_tasks, load_tools


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate raw tool-calling episodes.")
    parser.add_argument("--episodes", required=True, help="Path to episodes.jsonl")
    parser.add_argument("--tools", required=True, help="Path to the tool schema JSON file")
    parser.add_argument("--tasks-glob", required=True, help="Glob path for task JSON files")
    parser.add_argument("--output", required=True, help="Path to the output CSV")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks = {task.task_id: task for task in load_tasks(args.tasks_glob)}
    tools = {tool.name: tool for tool in load_tools(args.tools)}

    rows = []
    with Path(args.episodes).open("r", encoding="utf-8") as handle:
        for line in handle:
            episode = json.loads(line)
            task = tasks[episode["task_id"]]
            prediction = episode["prediction"]
            result = evaluate_prediction(
                sample_id=episode["sample_id"],
                task=task,
                variant_name=episode["variant_name"],
                predicted_tool=prediction.get("tool_name_pred"),
                predicted_args=prediction.get("arguments_pred", {}),
                tool_registry=tools,
            )
            rows.append(result.model_dump())

    pd.DataFrame(rows).to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
