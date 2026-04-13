from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List

from openai import OpenAI

from runner.prompting import to_openai_tools
from runner.schemas import ModelConfig, PredictionRecord, ToolSchema


class OpenAICompatibleChatToolClient:
    def __init__(self, config: ModelConfig) -> None:
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise ValueError(f"Environment variable {config.api_key_env} is not set.")

        base_url = os.getenv(config.base_url_env) if config.base_url_env else None
        self.config = config
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, messages: List[Dict[str, str]], tools: List[ToolSchema]) -> tuple[PredictionRecord, int, Dict[str, Any]]:
        openai_tools = to_openai_tools(tools)
        start = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_tokens=self.config.max_tokens,
            timeout=self.config.timeout_seconds,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)

        message = response.choices[0].message
        raw_response = response.model_dump()

        if not message.tool_calls:
            return (
                PredictionRecord(tool_name_pred=None, arguments_pred={}, raw_response=raw_response),
                latency_ms,
                _usage_to_dict(response),
            )

        tool_call = message.tool_calls[0]
        try:
            arguments = json.loads(tool_call.function.arguments or "{}")
            parse_error = None
        except json.JSONDecodeError as exc:
            arguments = {}
            parse_error = f"json_decode_error: {exc}"

        prediction = PredictionRecord(
            tool_name_pred=tool_call.function.name,
            arguments_pred=arguments,
            raw_response=raw_response,
            parse_error=parse_error,
        )
        return prediction, latency_ms, _usage_to_dict(response)


def _usage_to_dict(response: Any) -> Dict[str, Any]:
    usage = getattr(response, "usage", None)
    return usage.model_dump() if usage else {}


OpenAIChatToolClient = OpenAICompatibleChatToolClient
