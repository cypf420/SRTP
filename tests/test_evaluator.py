from evaluator.rules import evaluate_prediction
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
