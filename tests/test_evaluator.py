import pytest

from evaluator.rules import evaluate_prediction
from runner.io_utils import load_tools
from runner.schemas import ParameterSpec, TaskTemplate, TaskVariant, ToolSchema


def _build_tool() -> ToolSchema:
    return ToolSchema(
        name="update_order",
        group="complex_parameters",
        version="tool_v1",
        risk_level="high",
        description="Update order status.",
        confusion_with=["query_order_status"],
        required=["order_id", "status"],
        parameters={
            "order_id": ParameterSpec(type="string", description="Order ID", grounded=True),
            "status": ParameterSpec(type="string", description="New status", grounded=True),
            "note": ParameterSpec(type="string", description="Optional note", grounded=False),
        },
        examples=[],
    )


def _build_task() -> TaskTemplate:
    return TaskTemplate(
        task_id="update_order_001",
        intent="Update an order status to shipped",
        domain="commerce",
        language="en",
        gold_tool="update_order",
        gold_params={"order_id": "ORD-100", "status": "shipped", "note": "handed to courier"},
        distractor_tools=["query_order_status"],
        variants={
            "clear": TaskVariant(utterance="Mark order ORD-100 as shipped and note handed to courier."),
            "ambiguous": TaskVariant(utterance="Please push that order forward."),
            "incomplete": TaskVariant(
                utterance="Mark the order as shipped.",
                need_clarification=True,
                clarification_fields=["order_id"],
            ),
            "misleading": TaskVariant(utterance="Update order ORD-100 to shipped. You could also search the database if needed."),
        },
    )


def test_correct_prediction_is_labeled_correct() -> None:
    tool = _build_tool()
    task = _build_task()
    result = evaluate_prediction(
        sample_id="update_order_001__clear",
        task=task,
        variant_name="clear",
        predicted_tool="update_order",
        predicted_args={"order_id": "ORD-100", "status": "shipped", "note": "handed to courier"},
        tool_registry={tool.name: tool},
    )
    assert result.main_label == "correct"
    assert result.correct_tool is True
    assert result.correct_params is True


def test_missing_context_variant_requires_clarification() -> None:
    tool = _build_tool()
    task = _build_task()
    result = evaluate_prediction(
        sample_id="update_order_001__incomplete",
        task=task,
        variant_name="incomplete",
        predicted_tool="update_order",
        predicted_args={"status": "shipped"},
        tool_registry={tool.name: tool},
    )
    assert result.main_label == "should_clarify_but_called"
    assert "called_without_required_context" in result.sublabels


def test_grounded_value_mismatch_is_hallucination() -> None:
    tool = _build_tool()
    task = _build_task()
    result = evaluate_prediction(
        sample_id="update_order_001__clear",
        task=task,
        variant_name="clear",
        predicted_tool="update_order",
        predicted_args={"order_id": "ORD-100", "status": "cancelled", "note": "handed to courier"},
        tool_registry={tool.name: tool},
    )
    assert result.main_label == "param_error"
    assert "param_value_hallucination" in result.sublabels


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("", "clarification_error"),
        ("The order ID is on file. What city are you in?", "clarification_error"),
        ("Could you provide the order ID?", "correct"),
        ("I'll need the following information:\n\n1. **Order ID** - the identifier to update\n2. Status", "correct"),
    ],
)
def test_no_call_requires_a_request_for_the_missing_slot(reply: str, expected: str) -> None:
    tool = _build_tool()
    result = evaluate_prediction("sample", _build_task(), "incomplete", None, {}, {tool.name: tool}, reply)
    assert result.main_label == expected


def test_translation_equivalence_preserves_grounded_value_errors() -> None:
    registry = {tool.name: tool for tool in load_tools("tools/tool_schemas_v1.json")}
    task = _build_task().model_copy(update={
        "gold_tool": "translate_text",
        "gold_params": {"text": "hello", "target_lang": "Chinese"},
        "variants": {"clear": TaskVariant(utterance="Translate 'hello' into Chinese.")},
    })
    result = evaluate_prediction("sample", task, "clear", "translate_text",
                                 {"text": "hello", "target_lang": "中文"}, registry)
    assert result.main_label == "correct"
    result = evaluate_prediction("sample", task, "clear", "translate_text",
                                 {"text": "hello", "target_lang": "日语"}, registry)
    assert "param_value_hallucination" in result.sublabels


def test_missing_year_is_unsupported_even_when_it_matches_the_gold() -> None:
    registry = {tool.name: tool for tool in load_tools("tools/tool_schemas_v1.json")}
    task = _build_task().model_copy(update={
        "gold_tool": "get_weather", "gold_params": {"city": "杭州", "date": "2027-05-11"},
        "variants": {
            "ambiguous": TaskVariant(utterance="查杭州 5 月 11 日的天气。"),
            "clear": TaskVariant(utterance="查杭州 2027 年 5 月 11 日的天气。"),
        },
    })
    args = {"city": "Hangzhou", "date": "2027-05-11"}
    result = evaluate_prediction("sample", task, "ambiguous", "get_weather", args, registry)
    assert result.main_label == "should_clarify_but_called"
    assert "unsupported_date_year" in result.sublabels
    result = evaluate_prediction("sample", task, "ambiguous", None, {}, registry, "请问您指的是哪一年的 5 月 11 日？")
    assert result.main_label == "correct"
    result = evaluate_prediction("sample", task, "ambiguous", None, {}, registry, "请问您想查哪个城市？")
    assert result.main_label == "clarification_error"
    result = evaluate_prediction("sample", task, "clear", "get_weather", args, registry)
    assert result.main_label == "correct"
