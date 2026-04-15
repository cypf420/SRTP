from __future__ import annotations

import json
import os
import random
import time
from typing import Any, Dict, List

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

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
        rate_limit_retries = 0
        connection_retries = 0

        while True:
            start = time.perf_counter()
            try:
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
                break
            except RateLimitError as exc:
                if rate_limit_retries >= self.config.rate_limit_max_retries:
                    raise
                rate_limit_retries += 1
                sleep_seconds = self._compute_rate_limit_sleep(exc, rate_limit_retries)
                print(
                    f"[rate-limit] model={self.config.model_name} "
                    f"retry={rate_limit_retries}/{self.config.rate_limit_max_retries} "
                    f"sleep={sleep_seconds:.1f}s"
                )
                time.sleep(sleep_seconds)
            except (APIConnectionError, APITimeoutError) as exc:
                if connection_retries >= self.config.connection_error_max_retries:
                    raise
                connection_retries += 1
                sleep_seconds = self._compute_connection_error_sleep(connection_retries)
                print(
                    f"[connection-error] model={self.config.model_name} "
                    f"type={type(exc).__name__} "
                    f"retry={connection_retries}/{self.config.connection_error_max_retries} "
                    f"sleep={sleep_seconds:.1f}s"
                )
                time.sleep(sleep_seconds)
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

    def _compute_rate_limit_sleep(self, exc: RateLimitError, attempt: int) -> float:
        retry_after = _extract_retry_after_seconds(exc)
        if retry_after is not None:
            return retry_after

        return _compute_exponential_sleep(
            initial_seconds=self.config.rate_limit_backoff_initial_seconds,
            max_seconds=self.config.rate_limit_backoff_max_seconds,
            jitter_seconds=self.config.rate_limit_backoff_jitter_seconds,
            attempt=attempt,
        )

    def _compute_connection_error_sleep(self, attempt: int) -> float:
        return _compute_exponential_sleep(
            initial_seconds=self.config.connection_error_backoff_initial_seconds,
            max_seconds=self.config.connection_error_backoff_max_seconds,
            jitter_seconds=self.config.connection_error_backoff_jitter_seconds,
            attempt=attempt,
        )


def _extract_retry_after_seconds(exc: RateLimitError) -> float | None:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if not headers:
        return None

    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    if retry_after is None:
        return None

    try:
        return max(0.0, float(retry_after))
    except (TypeError, ValueError):
        return None


def _compute_exponential_sleep(
    initial_seconds: float,
    max_seconds: float,
    jitter_seconds: float,
    attempt: int,
) -> float:
    exponential = initial_seconds * (2 ** (attempt - 1))
    capped = min(exponential, max_seconds)
    jitter = random.uniform(0.0, jitter_seconds)
    return capped + jitter


def _usage_to_dict(response: Any) -> Dict[str, Any]:
    usage = getattr(response, "usage", None)
    return usage.model_dump() if usage else {}


OpenAIChatToolClient = OpenAICompatibleChatToolClient
