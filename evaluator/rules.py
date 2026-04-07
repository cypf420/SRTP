from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from runner.schemas import TaskTemplate, ToolSchema


class EvaluationResult(BaseModel):
    sample_id: str
    main_label: str
    sublabels: List[str] = Field(default_factory=list)
    correct_tool: bool
    correct_params: bool
    notes: List[str] = Field(default_factory=list)


def evaluate_prediction(
    sample_id: str,
    task: TaskTemplate,
    variant_name: str,
    predicted_tool: str | None,
    predicted_args: Dict[str, Any],
    tool_registry: Dict[str, ToolSchema],
) -> EvaluationResult:
    variant = task.variants[variant_name]
    sublabels: List[str] = []
    notes: List[str] = []

    if variant.need_clarification:
        if predicted_tool is None:
            return EvaluationResult(
                sample_id=sample_id,
                main_label="correct",
                sublabels=[],
                correct_tool=True,
                correct_params=True,
                notes=["clarification_expected_and_no_tool_called"],
            )
        return EvaluationResult(
            sample_id=sample_id,
            main_label="should_clarify_but_called",
            sublabels=["called_without_required_context"],
            correct_tool=False,
            correct_params=False,
            notes=[f"missing_fields={','.join(variant.clarification_fields)}"],
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
        if required_name not in predicted_args:
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
        if actual_value != expected_value:
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
