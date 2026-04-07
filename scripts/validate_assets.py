from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.io_utils import load_tasks, load_tools


def main() -> None:
    tools = load_tools("tools/tool_schemas_v1.json")
    tasks = load_tasks("tasks/base_tasks_v1/*.json")

    if len(tools) != 10:
        raise SystemExit(f"Expected 10 tools, found {len(tools)}")
    if len(tasks) != 50:
        raise SystemExit(f"Expected 50 base tasks, found {len(tasks)}")

    tool_names = {tool.name for tool in tools}
    for task in tasks:
        if task.gold_tool not in tool_names:
            raise SystemExit(f"Task {task.task_id} references unknown gold tool {task.gold_tool}")
        for distractor in task.distractor_tools:
            if distractor not in tool_names:
                raise SystemExit(f"Task {task.task_id} references unknown distractor tool {distractor}")
        for variant_name in ("clear", "ambiguous", "incomplete", "misleading"):
            if variant_name not in task.variants:
                raise SystemExit(f"Task {task.task_id} is missing the {variant_name} variant")

    print("Asset validation passed.")


if __name__ == "__main__":
    main()
