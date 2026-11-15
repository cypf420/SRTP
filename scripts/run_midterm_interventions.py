"""Run and summarize paired tool-calling interventions without executing tools."""

from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from datetime import date
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.client import OpenAICompatibleChatToolClient
from runner.io_utils import append_jsonl, load_model_config, load_tasks, load_text, load_tools, write_json
from runner.prompting import build_messages
from scripts.build_phase3_processed import MAIN_GLOB, assign_split

OUT = ROOT / "outputs" / "midterm" / "interventions"
TERRA_MODEL = "gpt-5.6-terra"
CONFIGS = {"qwen": "qwen2_5_7b_instruct", "glm": "glm_4_7", TERRA_MODEL: "gpt_5_6_terra"}
DATE_FIELDS = {"book_flight": "date", "change_flight": "new_date", "get_weather": "date"}
DESCRIPTION_ADDITIONS = {
    "search_web": "Use for public websites or public news, even if the request mentions an internal database. Excludes private records and internal documents.",
    "search_database": "Use to look up individual business records by name, ID, or field in a CRM or other structured system. Excludes public web pages and policy document retrieval.",
    "query_internal_docs": "Use to retrieve internal policy, manuals, procedures, or other unstructured documents. Excludes public websites and individual records in a structured system.",
}


def make_requests() -> dict:
    tasks = load_tasks(MAIN_GLOB)
    split = assign_split(tasks)
    available = [task for task in tasks if split[task.template_family] in {"train", "dev"}]
    system_prompt = load_text(ROOT / "prompts" / "system_prompt_v1.txt")
    registry = load_tools(ROOT / "tools" / "tool_schemas_v1.json")
    enhanced = [tool.model_copy(update={"description": f"{tool.description} {DESCRIPTION_ADDITIONS[tool.name]}"})
                if tool.name in DESCRIPTION_ADDITIONS else tool for tool in registry]
    cases = []
    for group, tool_fields in (("year", DATE_FIELDS), ("description", DESCRIPTION_ADDITIONS)):
        for tool_name in tool_fields:
            for language in ("zh", "en"):
                matching = [task for task in available if task.gold_tool == tool_name and task.language == language]
                first_in_family = {}
                for task in matching:
                    first_in_family.setdefault(task.template_family, task.task_id)
                matching.sort(key=lambda task: task.task_id != first_in_family[task.template_family])
                selected = 0
                for task in matching:
                    variant = "clear" if group == "year" else "misleading"
                    messages = build_messages(system_prompt, task, variant)
                    case = {"group": group, "case_id": task.task_id, "template_family": task.template_family,
                            "language": language, "expected_tool": task.gold_tool, "control_messages": messages,
                            "treatment_messages": messages}
                    if group == "year":
                        field = DATE_FIELDS[tool_name]
                        baseline = task.gold_params.get(field, "")
                        if not baseline or messages[-1]["content"].count(baseline) != 1:
                            continue
                        original = date.fromisoformat(baseline)
                        d = original.replace(year=2027)
                        short = f"{d.month}月{d.day}日" if language == "zh" else f"{calendar.month_name[d.month]} {d.day}"
                        long = f"{d.year}年{short}" if language == "zh" else f"{short}, {d.year}"
                        case.update({"date_field": field, "expected_date": d.isoformat(), "missing_year": short,
                                     "explicit_year": long})
                        for arm, replacement in (("control", short), ("treatment", long)):
                            user = {**messages[-1], "content": messages[-1]["content"].replace(baseline, replacement)}
                            case[f"{arm}_messages"] = [*messages[:-1], user]
                    cases.append(case)
                    selected += 1
                    if selected == 2:
                        break
                if selected != 2:
                    raise ValueError(f"Not enough cases: {group}, {tool_name}, {language}")
    return {"registry": [t.model_dump() for t in registry], "enhanced": [t.model_dump() for t in enhanced], "cases": cases}


def terra_response_model(raw_response: dict, observed: str | None) -> str:
    served = raw_response.get("model")
    if not isinstance(served, str) or not re.fullmatch(rf"{re.escape(TERRA_MODEL)}(?:-\d{{4}}-\d{{2}}-\d{{2}})?", served):
        raise ValueError(f"Expected GPT-5.6 Terra, served model: {served!r}")
    if observed is not None and served != observed:
        raise ValueError(f"Served model changed from {observed!r} to {served!r}")
    return served


def run(model: str, manifest: dict, plan_digest: str | None = None) -> None:
    from runner.schemas import ToolSchema

    config = load_model_config(ROOT / "configs" / "models" / f"{CONFIGS[model]}.yaml")
    config = config.model_copy(update={"timeout_seconds": 60, "connection_error_max_retries": 1, "rate_limit_max_retries": 0})
    is_terra = model == TERRA_MODEL
    if is_terra and (config.model_name, config.backend, config.api_key_env) != (TERRA_MODEL, "openai_chat", "OPENAI_API_KEY"):
        raise ValueError("The Terra experiment requires GPT-5.6 Terra on the official OpenAI API")
    client = OpenAICompatibleChatToolClient(config)
    run_path = OUT / f"{model}.jsonl"
    config_path = OUT / f"{model}_config.json"
    current_config = {**config.model_dump(), "served_model_id": None}
    if is_terra:
        current_config.update(endpoint=str(client.client.base_url), reasoning_effort="none", plan_sha256=plan_digest)
    if model == "qwen":
        import subprocess
        listing = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        current_config["served_model_id"] = next(
            (fields[1] for line in listing.stdout.splitlines() if (fields := line.split()) and fields[0] == config.model_name), None
        )
    if config_path.exists() and json.loads(config_path.read_text(encoding="utf-8")) != current_config:
        raise ValueError(f"Saved configuration differs for {model}")
    write_json(config_path, current_config)
    records = [json.loads(line) for line in run_path.read_text(encoding="utf-8").splitlines()] if run_path.exists() else []
    done = {(r["group"], r["case_id"], r["arm"]) for r in records}
    registries = {key: [ToolSchema.model_validate(item) for item in manifest[key]] for key in ("registry", "enhanced")}
    observed_model = None
    try:
        if is_terra:
            for record in records:
                observed_model = terra_response_model(record["prediction"]["raw_response"], observed_model)
        for index, case in enumerate(manifest["cases"]):
            for arm in (("control", "treatment") if index % 2 == 0 else ("treatment", "control")):
                key = (case["group"], case["case_id"], arm)
                if key in done:
                    continue
                tool_set = "enhanced" if case["group"] == "description" and arm == "treatment" else "registry"
                prediction, latency, usage = client.generate(case[f"{arm}_messages"], registries[tool_set])
                if is_terra:
                    observed_model = terra_response_model(prediction.raw_response, observed_model)
                append_jsonl(run_path, {"model": config.model_name, "group": key[0], "case_id": key[1], "arm": arm,
                                        "prediction": prediction.model_dump(), "latency_ms": latency, "usage": usage})
                done.add(key)
                print(f"{model}: {len(done)}/{2 * len(manifest['cases'])} {case['group']} {case['case_id']} {arm}", flush=True)
    except Exception as exc:
        status = {"type": type(exc).__name__, "status_code": getattr(exc, "status_code", None),
                  "provider_code": getattr(exc, "code", None), "completed": len(done)}
        write_json(OUT / f"{model}_failure.json", status)
        raise SystemExit(f"{model}: {status}") from None
    (OUT / f"{model}_failure.json").unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=[*CONFIGS, "prepare", "summarize"])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.model == "summarize":
        from scripts.summarize_midterm_interventions import summarize
        summarize(OUT)
        return
    plan_path = OUT / "plan.json"
    if args.model == TERRA_MODEL:
        if not plan_path.is_file():
            parser.error(f"The Terra experiment requires the frozen plan at {plan_path}")
        frozen_plan = plan_path.read_bytes()
        run(args.model, json.loads(frozen_plan), sha256(frozen_plan).hexdigest())
        return
    manifest = make_requests()
    if plan_path.exists():
        if manifest != json.loads(plan_path.read_text(encoding="utf-8")):
            raise ValueError("Current experimental inputs differ from the saved plan")
    else:
        write_json(plan_path, manifest)
    if args.model == "prepare":
        print(f"Saved {len(manifest['cases'])} paired cases to {plan_path}")
    else:
        run(args.model, manifest)


if __name__ == "__main__":
    main()
