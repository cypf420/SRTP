from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.client import OpenAICompatibleChatToolClient
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
    parser.add_argument(
        "--output",
        help="Optional explicit output JSON path. Defaults to outputs/smoke_tests/<timestamp>_<model>.json",
    )
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
    client = OpenAICompatibleChatToolClient(model_config)
    prediction, latency_ms, usage = client.generate(messages, tools)

    output_path = _resolve_output_path(args.output, model_config.model_name)
    payload = {
        "task_id": task.task_id,
        "variant": args.variant,
        "model_name": model_config.model_name,
        "predicted_tool": prediction.tool_name_pred,
        "predicted_args": prediction.arguments_pred,
        "latency_ms": latency_ms,
        "usage": usage,
        "raw_response": prediction.raw_response,
        "parse_error": prediction.parse_error,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("task_id:", task.task_id)
    print("variant:", args.variant)
    print("predicted_tool:", prediction.tool_name_pred)
    print("predicted_args:", prediction.arguments_pred)
    print("latency_ms:", latency_ms)
    print("usage:", usage)
    print("saved_to:", output_path)


def _resolve_output_path(explicit_output: str | None, model_name: str) -> Path:
    if explicit_output:
        return Path(explicit_output)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model_name = re.sub(r"[^A-Za-z0-9._-]+", "_", model_name)
    return ROOT / "outputs" / "smoke_tests" / f"{timestamp}_{safe_model_name}.json"


if __name__ == "__main__":
    main()
