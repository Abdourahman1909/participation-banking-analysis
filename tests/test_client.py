"""Offline proof of the model-provider seam (ADR 0019).

No network / no GPU: an httpx.MockTransport fakes the OpenAI-compatible
endpoint, and we assert get_model() selects the right client and
OpenAICompatClient parses/normalizes responses correctly. Run either way:

    uv run python tests/test_client.py
    uv run pytest tests/test_client.py
"""

from __future__ import annotations

import json

import httpx

from banking_analysis.extraction.client import (
    OllamaClient,
    OpenAICompatClient,
    get_model,
)


def _mock_client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_get_model_defaults_to_ollama(monkeypatch=None):
    import os

    os.environ.pop("MODEL_PROVIDER", None)
    assert isinstance(get_model(), OllamaClient)


def test_get_model_selects_external_when_asked():
    import os

    os.environ["MODEL_PROVIDER"] = "groq"
    os.environ["MODEL_API_KEY"] = "test-key"
    try:
        assert isinstance(get_model(), OpenAICompatClient)
    finally:
        os.environ.pop("MODEL_PROVIDER", None)
        os.environ.pop("MODEL_API_KEY", None)


def test_get_model_rejects_unknown_provider():
    import os

    os.environ["MODEL_PROVIDER"] = "banana"
    try:
        raised = False
        try:
            get_model()
        except ValueError:
            raised = True
        assert raised, "unknown provider should raise"
    finally:
        os.environ.pop("MODEL_PROVIDER", None)


def test_external_client_needs_api_key():
    import os

    os.environ.pop("MODEL_API_KEY", None)
    raised = False
    try:
        OpenAICompatClient(api_key="")
    except RuntimeError:
        raised = True
    assert raised, "missing MODEL_API_KEY should raise"


def test_complete_parses_openai_response():
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        # JSON mode requested, auth header present
        assert body["response_format"] == {"type": "json_object"}
        assert request.headers["authorization"] == "Bearer k"
        return httpx.Response(200, json={
            "choices": [{"message": {"role": "assistant", "content": '{"x": 1}'}}]
        })

    c = OpenAICompatClient(api_key="k", client=_mock_client(handler))
    assert c.complete("sys", "user") == '{"x": 1}'


def test_chat_normalizes_tool_calls_to_ollama_shape():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "choices": [{"message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_1", "type": "function",
                    "function": {"name": "get_campaigns", "arguments": "{}"},
                }],
            }}]
        })

    c = OpenAICompatClient(api_key="k", client=_mock_client(handler))
    msg = c.chat([{"role": "user", "content": "hi"}], tools=[{"x": 1}])
    # Same shape OllamaClient.chat returns: dict with content + tool_calls.
    assert msg["content"] == ""              # None coerced to ""
    assert msg["tool_calls"][0]["function"]["name"] == "get_campaigns"


def _run_all() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}  {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed


if __name__ == "__main__":
    raise SystemExit(_run_all())
