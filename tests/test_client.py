from types import SimpleNamespace

import runner.client as client_module
from runner.client import OpenAICompatibleChatToolClient
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
