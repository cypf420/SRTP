"""Summarize saved paired requests and model responses without new API calls."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

from evaluator.clarification import missing_reply_fields
from evaluator.rules import assistant_reply
from runner.io_utils import write_json


def date_outcome(case: dict, arm: str, prediction: dict) -> str:
    tool = prediction.get("tool_name_pred")
    field = case["date_field"]
    if tool is None:
        reply = assistant_reply(prediction)
        return "asked_year" if not missing_reply_fields(reply, {field}, field) else "other_no_call"
    if tool != case["expected_tool"]:
        return "wrong_tool"
    value = prediction.get("arguments_pred", {}).get(field)
    try:
        emitted = date.fromisoformat(value)
    except (TypeError, ValueError):
        return "called_without_valid_date"
    if arm == "control":
        return "unsupported_year"
    expected = date.fromisoformat(case["expected_date"])
    if emitted.year != expected.year:
        return "unsupported_year"
    return "correct_date" if emitted == expected else "wrong_month_day"


def tool_outcome(case: dict, prediction: dict) -> str:
    tool = prediction.get("tool_name_pred")
    if tool is None:
        return "no_call"
    return "correct_tool" if tool == case["expected_tool"] else "wrong_tool"


def summarize(directory: Path) -> None:
    manifest = json.loads((directory / "plan.json").read_text(encoding="utf-8"))
    summary = {}
    pair_rows = []
    for model_path in sorted(directory.glob("*.jsonl")):
        episodes = [json.loads(line) for line in model_path.read_text(encoding="utf-8").splitlines()]
        response = {(r["group"], r["case_id"], r["arm"]): r for r in episodes}
        expected_keys = {(case["group"], case["case_id"], arm)
                         for case in manifest["cases"] for arm in ("control", "treatment")}
        if len(response) != len(episodes) or not response.keys() <= expected_keys:
            raise ValueError(f"Unexpected or duplicate rows in {model_path.name}")
        metrics = {}
        for group in sorted({case["group"] for case in manifest["cases"]}):
            cases = [case for case in manifest["cases"] if case["group"] == group]
            pairs = []
            for case in cases:
                prediction = {arm: response.get((group, case["case_id"], arm), {}).get("prediction")
                              for arm in ("control", "treatment")}
                if any(item is None for item in prediction.values()):
                    continue
                outcomes = {}
                for arm, item in prediction.items():
                    if item.get("parse_error") and group == "year":
                        outcomes[arm] = "parse_error"
                    else:
                        outcomes[arm] = date_outcome(case, arm, item) if group == "year" else tool_outcome(case, item)
                row = {"model": model_path.stem, "group": group, "case_id": case["case_id"],
                       "template_family": case["template_family"], "expected_tool": case["expected_tool"],
                       "language": case["language"], **outcomes}
                pairs.append(row)
            pair_rows.extend(pairs)
            metrics[group] = {"planned_pairs": len(cases), "complete_pairs": len(pairs),
                              "families": len({row["template_family"] for row in pairs}),
                              "control": dict(Counter(row["control"] for row in pairs)),
                              "treatment": dict(Counter(row["treatment"] for row in pairs)),
                              "transitions": [{"control": c, "treatment": t, "pairs": n} for (c, t), n in
                                              sorted(Counter((row["control"], row["treatment"]) for row in pairs).items())]}
        summary[model_path.stem] = metrics
    failed_models = {path.name.removesuffix("_failure.json"): json.loads(path.read_text(encoding="utf-8"))
                     for path in directory.glob("*_failure.json")}
    summary = {"models": summary, "endpoint_failures": failed_models}
    write_json(directory / "summary.json", summary)
    write_json(directory / "pairs.json", pair_rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
