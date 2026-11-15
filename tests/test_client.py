from types import SimpleNamespace

import httpx
from openai import OpenAI

import runner.client as client_module
from runner.client import OpenAICompatibleChatToolClient
from runner.io_utils import load_model_config, load_tools
from runner.schemas import ModelConfig


def test_generate_retries_after_rate_limit(monkeypatch) -> None:
    monkeypatch.setenv("TEST_GLM_API_KEY", "dummy")
    monkeypatch.setattr(client_module, "to_openai_tools", lambda tools: [])

    class DummyRateLimitError(Exception):
        pass

    monkeypatch.setattr(client_module, "RateLimitError", DummyRateLimitError)

    state = {"calls": 0}
    sleeps: list[float] = []

    class FakeResponse:
        def __init__(self) -> None:
            self.choices = [SimpleNamespace(message=SimpleNamespace(tool_calls=None))]
            self.usage = None

        def model_dump(self):
            return {"id": "resp_ok"}

    class FakeCompletions:
        def create(self, **kwargs):
            state["calls"] += 1
            if state["calls"] == 1:
                raise DummyRateLimitError("429")
            return FakeResponse()

    class FakeOpenAI:
        def __init__(self, **kwargs) -> None:
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(client_module, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(client_module.time, "sleep", lambda seconds: sleeps.append(seconds))

    config = ModelConfig(
        backend="openai_compatible_chat",
        model_name="glm-4.7",
        api_key_env="TEST_GLM_API_KEY",
        rate_limit_max_retries=2,
        rate_limit_backoff_initial_seconds=1.0,
        rate_limit_backoff_max_seconds=10.0,
        rate_limit_backoff_jitter_seconds=0.0,
    )
    client = OpenAICompatibleChatToolClient(config)

    prediction, latency_ms, usage = client.generate([{"role": "user", "content": "ping"}], [])

    assert state["calls"] == 2
    assert sleeps == [1.0]
    assert prediction.tool_name_pred is None
    assert latency_ms >= 0
    assert usage == {}


def test_generate_retries_after_connection_error(monkeypatch) -> None:
    monkeypatch.setenv("TEST_GLM_API_KEY", "dummy")
    monkeypatch.setattr(client_module, "to_openai_tools", lambda tools: [])

    class DummyAPIConnectionError(Exception):
        pass

    class DummyAPITimeoutError(Exception):
        pass

    monkeypatch.setattr(client_module, "APIConnectionError", DummyAPIConnectionError)
    monkeypatch.setattr(client_module, "APITimeoutError", DummyAPITimeoutError)

    state = {"calls": 0}
    sleeps: list[float] = []

    class FakeResponse:
        def __init__(self) -> None:
            self.choices = [SimpleNamespace(message=SimpleNamespace(tool_calls=None))]
            self.usage = None

        def model_dump(self):
            return {"id": "resp_ok"}

    class FakeCompletions:
        def create(self, **kwargs):
            state["calls"] += 1
            if state["calls"] == 1:
                raise DummyAPIConnectionError("connection")
            return FakeResponse()

    class FakeOpenAI:
        def __init__(self, **kwargs) -> None:
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(client_module, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(client_module.time, "sleep", lambda seconds: sleeps.append(seconds))

    config = ModelConfig(
        backend="openai_compatible_chat",
        model_name="glm-4.7",
        api_key_env="TEST_GLM_API_KEY",
        connection_error_max_retries=2,
        connection_error_backoff_initial_seconds=2.0,
        connection_error_backoff_max_seconds=10.0,
        connection_error_backoff_jitter_seconds=0.0,
    )
    client = OpenAICompatibleChatToolClient(config)

    prediction, latency_ms, usage = client.generate([{"role": "user", "content": "ping"}], [])

    assert state["calls"] == 2
    assert sleeps == [2.0]
    assert prediction.tool_name_pred is None
    assert latency_ms >= 0
    assert usage == {}


def test_terra_sends_function_tools_to_official_chat_completions(monkeypatch) -> None:
    import json

    monkeypatch.setenv("OPENAI_API_KEY", "offline-test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    messages = [{"role": "user", "content": "Check the weather in Seattle."}]
    tools = [tool for tool in load_tools("tools/tool_schemas_v1.json") if tool.name == "get_weather"]

    def respond(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://api.openai.com/v1/chat/completions"
        body = json.loads(request.content)
        assert body["model"] == "gpt-5.6-terra"
        assert body["reasoning_effort"] == "none"
        assert body["max_completion_tokens"] == 512
        assert "max_tokens" not in body
        assert body["messages"] == messages
        assert body["tool_choice"] == "auto"
        assert body["tools"][0]["function"]["name"] == "get_weather"
        return httpx.Response(200, json={
            "id": "offline-test", "object": "chat.completion", "created": 0, "model": "gpt-5.6-terra",
            "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {
                "role": "assistant", "content": None,
                "tool_calls": [{"id": "offline-call", "type": "function", "function": {
                    "name": "get_weather", "arguments": '{"city":"Seattle"}',
                }}],
            }}],
        })

    with httpx.Client(transport=httpx.MockTransport(respond)) as transport_client:
        monkeypatch.setattr(client_module, "OpenAI", lambda **kwargs: OpenAI(**kwargs, http_client=transport_client))
        config = load_model_config("configs/models/gpt_5_6_terra.yaml")
        prediction, _, _ = OpenAICompatibleChatToolClient(config).generate(messages, tools)
    assert prediction.tool_name_pred == "get_weather"
    assert prediction.arguments_pred == {"city": "Seattle"}
    assert prediction.raw_response["model"] == "gpt-5.6-terra"
