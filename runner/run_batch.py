from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.client import OpenAIChatToolClient
from runner.io_utils import load_model_config, load_run_config, load_tasks, load_text, load_tools, write_json, write_jsonl
from runner.metadata import collect_git_metadata, make_run_id, utc_now_iso
from runner.prompting import build_messages
from runner.schemas import EpisodeRecord, TaskTemplate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a batch of tool-calling tasks.")
    parser.add_argument("--config", required=True, help="Path to a run config YAML file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_config = load_run_config(args.config)
    model_config = load_model_config(run_config.model_config_path)
    tools = load_tools(run_config.tools_path)
    tasks = load_tasks(run_config.tasks_glob)
    system_prompt = load_text(run_config.prompt_path)
    run_id = make_run_id(run_config.run_name)
    git_meta = collect_git_metadata(ROOT)
    started_at = utc_now_iso()

    if run_config.task_limit is not None:
        tasks = tasks[: run_config.task_limit]

    client = OpenAIChatToolClient(model_config)
    episode_rows = []

    for task in tqdm(tasks, desc="tasks"):
        episode_rows.extend(_run_task(task, run_id, run_config.variant_names, tools, system_prompt, client, model_config.model_name))

    run_dir = Path(run_config.output_dir) / run_id
    if run_dir.exists() and not run_config.overwrite:
        raise FileExistsError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl(run_dir / "episodes.jsonl", [row.model_dump() for row in episode_rows])
    write_json(
        run_dir / "run_manifest.json",
        {
            "run_id": run_id,
            "run_name": run_config.run_name,
            "started_at": started_at,
            "finished_at": utc_now_iso(),
            "model_name": model_config.model_name,
            "prompt_version": Path(run_config.prompt_path).stem,
            "tool_versions": sorted({tool.version for tool in tools}),
            "task_versions": sorted({task.version for task in tasks}),
            "prompt_path": run_config.prompt_path,
            "tools_path": run_config.tools_path,
            "tasks_glob": run_config.tasks_glob,
            "variant_names": run_config.variant_names,
            "task_count": len(tasks),
            "episode_count": len(episode_rows),
            "git": git_meta,
            "config_snapshot_paths": {
                "run_config": "run_config_snapshot.yaml",
                "model_config": "model_config_snapshot.yaml",
                "prompt": "system_prompt_snapshot.txt",
            },
        },
    )
    (run_dir / "run_config_snapshot.yaml").write_text(Path(args.config).read_text(encoding="utf-8"), encoding="utf-8")
    (run_dir / "model_config_snapshot.yaml").write_text(Path(run_config.model_config_path).read_text(encoding="utf-8"), encoding="utf-8")
    (run_dir / "system_prompt_snapshot.txt").write_text(system_prompt, encoding="utf-8")


def _run_task(
    task: TaskTemplate,
    run_id: str,
    variant_names: List[str],
    tools,
    system_prompt: str,
    client: OpenAIChatToolClient,
    model_name: str,
) -> List[EpisodeRecord]:
    rows: List[EpisodeRecord] = []
    for variant_name in variant_names:
        if variant_name not in task.variants:
            continue
        messages = build_messages(system_prompt, task, variant_name)
        prediction, latency_ms, usage = client.generate(messages, tools)
        rows.append(
            EpisodeRecord(
                run_id=run_id,
                sample_id=f"{task.task_id}__{variant_name}",
                task_id=task.task_id,
                variant_name=variant_name,
                model_name=model_name,
                prompt_version="prompt_v1",
                tool_version="tool_v1",
                task_version=task.version,
                messages=messages,
                tools=[tool.name for tool in tools],
                prediction=prediction,
                latency_ms=latency_ms,
                usage=usage,
            )
        )
    return rows


if __name__ == "__main__":
    main()
