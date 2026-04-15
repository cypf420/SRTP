from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.client import OpenAICompatibleChatToolClient
from runner.io_utils import append_jsonl, load_jsonl_sample_ids, load_model_config, load_run_config, load_tasks, load_text, load_tools, write_json
from runner.metadata import collect_git_metadata, make_run_id, utc_now_iso
from runner.prompting import build_messages
from runner.schemas import EpisodeRecord, TaskTemplate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a batch of tool-calling tasks.")
    parser.add_argument("--config", required=True, help="Path to a run config YAML file.")
    parser.add_argument("--run-id", help="Reuse a specific run_id. Required for true resume on an interrupted run.")
    parser.add_argument("--resume", action="store_true", help="Resume from an existing run directory and skip completed sample_ids.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_config = load_run_config(args.config)
    model_config = load_model_config(run_config.model_config_path)
    tools = load_tools(run_config.tools_path)
    tasks = load_tasks(run_config.tasks_glob)
    system_prompt = load_text(run_config.prompt_path)
    run_id = args.run_id or make_run_id(run_config.run_name)
    git_meta = collect_git_metadata(ROOT)

    if run_config.task_limit is not None:
        tasks = tasks[: run_config.task_limit]

    run_dir = Path(run_config.output_dir) / run_id
    episodes_path = run_dir / "episodes.jsonl"
    manifest_path = run_dir / "run_manifest.json"

    if run_dir.exists() and not args.resume and not run_config.overwrite:
        raise FileExistsError(
            f"Run directory already exists: {run_dir}. Use --resume --run-id {run_id} to continue it."
        )

    run_dir.mkdir(parents=True, exist_ok=True)
    if run_dir.exists() and run_config.overwrite and not args.resume:
        _clear_run_outputs(run_dir)
    existing_manifest = _load_existing_manifest(manifest_path)
    started_at = existing_manifest.get("started_at", utc_now_iso()) if existing_manifest else utc_now_iso()
    completed_sample_ids = load_jsonl_sample_ids(episodes_path) if args.resume else set()
    print(f"run_id: {run_id}")
    if completed_sample_ids:
        print(f"resume_mode: skipping {len(completed_sample_ids)} completed sample_ids")

    _write_config_snapshots(run_dir, args.config, run_config.model_config_path, system_prompt)
    client = OpenAICompatibleChatToolClient(model_config)
    _write_manifest(
        manifest_path=manifest_path,
        run_id=run_id,
        run_config=run_config,
        model_name=model_config.model_name,
        git_meta=git_meta,
        task_versions=sorted({task.version for task in tasks}),
        tool_versions=sorted({tool.version for tool in tools}),
        task_count=len(tasks),
        started_at=started_at,
        status="running",
        episode_count=len(completed_sample_ids),
        completed_sample_count=len(completed_sample_ids),
        resume_mode=args.resume,
    )

    try:
        for task in tqdm(tasks, desc="tasks"):
            _run_task(
                task=task,
                run_id=run_id,
                variant_names=run_config.variant_names,
                tools=tools,
                system_prompt=system_prompt,
                client=client,
                model_name=model_config.model_name,
                episodes_path=episodes_path,
                completed_sample_ids=completed_sample_ids,
            )
    except Exception as exc:
        _write_manifest(
            manifest_path=manifest_path,
            run_id=run_id,
            run_config=run_config,
            model_name=model_config.model_name,
            git_meta=git_meta,
            task_versions=sorted({task.version for task in tasks}),
            tool_versions=sorted({tool.version for tool in tools}),
            task_count=len(tasks),
            started_at=started_at,
            status="failed",
            episode_count=len(completed_sample_ids),
            completed_sample_count=len(completed_sample_ids),
            resume_mode=args.resume,
            error={"type": type(exc).__name__, "message": str(exc)},
        )
        raise
    except KeyboardInterrupt:
        _write_manifest(
            manifest_path=manifest_path,
            run_id=run_id,
            run_config=run_config,
            model_name=model_config.model_name,
            git_meta=git_meta,
            task_versions=sorted({task.version for task in tasks}),
            tool_versions=sorted({tool.version for tool in tools}),
            task_count=len(tasks),
            started_at=started_at,
            status="interrupted",
            episode_count=len(completed_sample_ids),
            completed_sample_count=len(completed_sample_ids),
            resume_mode=args.resume,
        )
        raise SystemExit("Run interrupted. Re-run with the same --run-id and --resume to continue.")

    _write_manifest(
        manifest_path=manifest_path,
        run_id=run_id,
        run_config=run_config,
        model_name=model_config.model_name,
        git_meta=git_meta,
        task_versions=sorted({task.version for task in tasks}),
        tool_versions=sorted({tool.version for tool in tools}),
        task_count=len(tasks),
        started_at=started_at,
        status="completed",
        episode_count=len(completed_sample_ids),
        completed_sample_count=len(completed_sample_ids),
        resume_mode=args.resume,
    )


def _run_task(
    task: TaskTemplate,
    run_id: str,
    variant_names: List[str],
    tools,
    system_prompt: str,
    client: OpenAICompatibleChatToolClient,
    model_name: str,
    episodes_path: Path,
    completed_sample_ids: set[str],
) -> int:
    new_rows = 0
    for variant_name in variant_names:
        if variant_name not in task.variants:
            continue
        sample_id = f"{task.task_id}__{variant_name}"
        if sample_id in completed_sample_ids:
            continue
        messages = build_messages(system_prompt, task, variant_name)
        prediction, latency_ms, usage = client.generate(messages, tools)
        row = EpisodeRecord(
            run_id=run_id,
            sample_id=sample_id,
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
        append_jsonl(episodes_path, row.model_dump())
        completed_sample_ids.add(sample_id)
        new_rows += 1
    return new_rows


def _load_existing_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_config_snapshots(run_dir: Path, run_config_path: str, model_config_path: str, system_prompt: str) -> None:
    (run_dir / "run_config_snapshot.yaml").write_text(Path(run_config_path).read_text(encoding="utf-8"), encoding="utf-8")
    (run_dir / "model_config_snapshot.yaml").write_text(Path(model_config_path).read_text(encoding="utf-8"), encoding="utf-8")
    (run_dir / "system_prompt_snapshot.txt").write_text(system_prompt, encoding="utf-8")


def _write_manifest(
    manifest_path: Path,
    run_id: str,
    run_config,
    model_name: str,
    git_meta: dict,
    task_versions: List[str],
    tool_versions: List[str],
    task_count: int,
    started_at: str,
    status: str,
    episode_count: int,
    completed_sample_count: int,
    resume_mode: bool,
    error: dict | None = None,
) -> None:
    payload = {
        "run_id": run_id,
        "run_name": run_config.run_name,
        "status": status,
        "resume_mode": resume_mode,
        "started_at": started_at,
        "finished_at": utc_now_iso(),
        "model_name": model_name,
        "prompt_version": Path(run_config.prompt_path).stem,
        "tool_versions": tool_versions,
        "task_versions": task_versions,
        "prompt_path": run_config.prompt_path,
        "tools_path": run_config.tools_path,
        "tasks_glob": run_config.tasks_glob,
        "variant_names": run_config.variant_names,
        "task_count": task_count,
        "episode_count": episode_count,
        "completed_sample_count": completed_sample_count,
        "git": git_meta,
        "config_snapshot_paths": {
            "run_config": "run_config_snapshot.yaml",
            "model_config": "model_config_snapshot.yaml",
            "prompt": "system_prompt_snapshot.txt",
        },
    }
    if error is not None:
        payload["error"] = error
    write_json(manifest_path, payload)


def _clear_run_outputs(run_dir: Path) -> None:
    for filename in (
        "episodes.jsonl",
        "run_manifest.json",
        "run_config_snapshot.yaml",
        "model_config_snapshot.yaml",
        "system_prompt_snapshot.txt",
    ):
        target = run_dir / filename
        if target.exists():
            target.unlink()


if __name__ == "__main__":
    main()
