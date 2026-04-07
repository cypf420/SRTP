from __future__ import annotations

from typing import Dict, List

from runner.schemas import TaskTemplate, TaskVariant, ToolSchema


def build_messages(system_prompt: str, task: TaskTemplate, variant_name: str) -> List[Dict[str, str]]:
    variant: TaskVariant = task.variants[variant_name]
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(task.dialog_context)
    messages.append({"role": "user", "content": variant.utterance})
    return messages


def to_openai_tools(tools: List[ToolSchema]) -> List[dict]:
    converted: List[dict] = []
    for tool in tools:
        properties = {}
        for name, spec in tool.parameters.items():
            schema: dict = {
                "type": spec.type,
                "description": spec.description,
            }
            if spec.enum is not None:
                schema["enum"] = spec.enum
            if spec.minimum is not None:
                schema["minimum"] = spec.minimum
            if spec.maximum is not None:
                schema["maximum"] = spec.maximum
            properties[name] = schema
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": tool.required,
                        "additionalProperties": False,
                    },
                },
            }
        )
    return converted
