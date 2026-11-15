from __future__ import annotations

from datetime import date
from typing import Any, Dict, List
from unicodedata import normalize

from pydantic import BaseModel, Field

from evaluator.clarification import expected_clarification, missing_reply_fields
from runner.schemas import TaskTemplate, ToolSchema

LANGUAGE_ALIASES = {
    "chinese": "chinese", "中文": "chinese", "汉语": "chinese", "mandarin": "chinese",
    "english": "english", "英语": "english", "英文": "english",
    "japanese": "japanese", "日语": "japanese", "日文": "japanese",
    "spanish": "spanish", "西班牙语": "spanish", "西语": "spanish", "español": "spanish",
}
CITY_ALIASES = {
    "北京": "beijing", "成都": "chengdu", "广州": "guangzhou", "杭州": "hangzhou",
    "南京": "nanjing", "上海": "shanghai", "三亚": "sanya", "西雅图": "seattle",
    "深圳": "shenzhen", "旧金山": "san francisco", "纽约": "new york", "东京": "tokyo",
}


class EvaluationResult(BaseModel):
    sample_id: str
    main_label: str
    sublabels: List[str] = Field(default_factory=list)
    correct_tool: bool
    correct_params: bool
    notes: List[str] = Field(default_factory=list)


def assistant_reply(prediction: dict) -> str:
    raw = prediction.get("raw_response")
    choices = raw.get("choices") if isinstance(raw, dict) else None
    reply = choices[0].get("message", {}).get("content") if choices else None
    return reply if isinstance(reply, str) else ""


def _equivalent(field: str, actual: Any, expected: Any) -> bool:
    if actual == expected:
        return True
    if not isinstance(actual, str) or not isinstance(expected, str):
        return False
    values = [" ".join(normalize("NFKC", value).casefold().split()) for value in (actual, expected)]
    if field == "target_lang":
        return LANGUAGE_ALIASES.get(values[0], values[0]) == LANGUAGE_ALIASES.get(values[1], values[1])
    if field in {"city", "origin", "destination"}:
        return CITY_ALIASES.get(values[0], values[0]) == CITY_ALIASES.get(values[1], values[1])
    # Preserve exact identifiers, date serialization, enum values and free-text golds.
    return False


def _contains_full_date(value: Any) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except (ValueError, TypeError):
        return False


def evaluate_prediction(
    sample_id: str,
    task: TaskTemplate,
    variant_name: str,
    predicted_tool: str | None,
    predicted_args: Dict[str, Any],
    tool_registry: Dict[str, ToolSchema],
    reply: str = "",
) -> EvaluationResult:
    variant = task.variants[variant_name]
    expected_fields, year_field = expected_clarification(task, variant_name)
    sublabels: List[str] = []
    notes: List[str] = []

    if expected_fields or variant.need_clarification:
        if predicted_tool is None:
            missing = missing_reply_fields(reply, expected_fields, year_field)
            if not reply.strip() or missing:
                return EvaluationResult(
                    sample_id=sample_id,
                    main_label="clarification_error",
                    sublabels=["empty_clarification_reply" if not reply.strip() else "missing_clarification_fields"],
                    correct_tool=True,
                    correct_params=False,
                    notes=[f"unasked_fields={','.join(sorted(missing))}"],
                )
            return EvaluationResult(
                sample_id=sample_id,
                main_label="correct",
                sublabels=[],
                correct_tool=True,
                correct_params=True,
                notes=["expected_fields_asked"],
            )
        sublabels = ["called_without_required_context"]
        if year_field and predicted_tool == task.gold_tool and _contains_full_date(predicted_args.get(year_field)):
            sublabels += ["unsupported_date_year", "param_value_hallucination"]
        return EvaluationResult(
            sample_id=sample_id,
            main_label="should_clarify_but_called",
            sublabels=sublabels,
            correct_tool=False,
            correct_params=False,
            notes=[f"missing_fields={','.join(sorted(expected_fields))}"],
        )

    if predicted_tool is None:
        return EvaluationResult(
            sample_id=sample_id,
            main_label="wrong_tool",
            sublabels=["no_tool_called"],
            correct_tool=False,
            correct_params=False,
            notes=["tool_call_expected_but_missing"],
        )

    if predicted_tool != task.gold_tool:
        if predicted_tool in tool_registry and tool_registry[predicted_tool].risk_level == "high":
            sublabels.append("high_risk_tool_misuse")
        return EvaluationResult(
            sample_id=sample_id,
            main_label="wrong_tool",
            sublabels=sublabels,
            correct_tool=False,
            correct_params=False,
            notes=[f"expected={task.gold_tool}", f"predicted={predicted_tool}"],
        )

    tool = tool_registry[predicted_tool]
    for required_name in tool.required:
        required_value = predicted_args.get(required_name)
        if required_value is None or (isinstance(required_value, str) and not required_value.strip()):
            sublabels.append("missing_required_param")
            notes.append(f"missing={required_name}")

    for arg_name in predicted_args:
        if arg_name not in tool.parameters:
            sublabels.append("extra_param")
            notes.append(f"extra={arg_name}")

    for arg_name, expected_value in task.gold_params.items():
        if arg_name not in predicted_args:
            continue
        actual_value = predicted_args[arg_name]
        param_spec = tool.parameters[arg_name]
        if not _matches_type(actual_value, param_spec.type):
            sublabels.append("param_type_error")
            notes.append(f"type_error={arg_name}")
            continue
        if not _equivalent(arg_name, actual_value, expected_value):
            if param_spec.grounded:
                sublabels.append("param_value_hallucination")
                notes.append(f"value_mismatch={arg_name}")
            else:
                sublabels.append("param_value_mismatch")
                notes.append(f"value_mismatch={arg_name}")

    if sublabels:
        return EvaluationResult(
            sample_id=sample_id,
            main_label="param_error",
            sublabels=sorted(set(sublabels)),
            correct_tool=True,
            correct_params=False,
            notes=notes,
        )

    return EvaluationResult(
        sample_id=sample_id,
        main_label="correct",
        sublabels=[],
        correct_tool=True,
        correct_params=True,
        notes=[],
    )


def _matches_type(value: Any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return False
