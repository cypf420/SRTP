from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.client import OpenAIChatToolClient
from runner.io_utils import load_model_config, load_tasks, load_text, load_tools
from runner.prompting import build_messages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one tool-calling smoke test.")
    parser.add_argument("--model-config", required=True, help="Path to a model config YAML file.")
    parser.add_argument("--tools", default="tools/tool_schemas_v1.json", help="Path to tool schemas.")
    parser.add_argument("--tasks-glob", default="tasks/base_tasks_v1/*.json", help="Glob for task JSON files.")
    parser.add_argument("--prompt", default="prompts/system_prompt_v1.txt", help="Path to the system prompt file.")
    parser.add_argument("--task-id", default="query_order_status_001", help="Task ID to run.")
    parser.add_argument("--variant", default="clear", help="Variant name to run.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_config = load_model_config(args.model_config)
    tools = load_tools(args.tools)
    tasks = {task.task_id: task for task in load_tasks(args.tasks_glob)}
    system_prompt = load_text(args.prompt)

    if args.task_id not in tasks:
        raise SystemExit(f"Unknown task_id: {args.task_id}")

    task = tasks[args.task_id]
    messages = build_messages(system_prompt, task, args.variant)
    client = OpenAIChatToolClient(model_config)
    prediction, latency_ms, usage = client.generate(messages, tools)

    print("task_id:", task.task_id)
    print("variant:", args.variant)
    print("predicted_tool:", prediction.tool_name_pred)
    print("predicted_args:", prediction.arguments_pred)
    print("latency_ms:", latency_ms)
    print("usage:", usage)


if __name__ == "__main__":
    main()
