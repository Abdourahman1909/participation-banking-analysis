"""Layer 2 — model client (ADR 0005, 0015, 0019).

Talks to a chat model over HTTP. The model's *location* is config, not code
(`OLLAMA_URL`), so the model can live on a teammate's GPU laptop (ADR 0015)
while this code runs anywhere. The `ChatModel` Protocol lets the extractor be
tested with a fake model offline — no GPU needed (ADR 0016).

Two implementations, selected by `get_model()` via `MODEL_PROVIDER`:
- `OllamaClient` (default) — local, offline, on-prem. The ONLY provider valid
  for the competition submission (spec §5.9, ADR 0009).
- `OpenAICompatClient` — an external OpenAI-compatible API (Groq, OpenRouter,
  …). DEV/TEST ONLY, for use while the GPU machine is being set up. Never the
  default, never in the competition config (ADR 0019).
"""

from __future__ import annotations

import os
import sys
from typing import Protocol

import httpx


class ChatModel(Protocol):
    """Minimal interface the extractor needs. Real impls: OllamaClient,
    OpenAICompatClient. Tests pass a fake returning canned JSON."""

    def complete(self, system: str, user: str) -> str: ...


class OllamaClient:
    """Calls Ollama's /api/chat with JSON-forced, deterministic decoding."""

    def __init__(
        self,
        url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        # Default to localhost; point at the GPU laptop via OLLAMA_URL (ADR 0015).
        self.url = (url or os.environ.get("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        # Model size (7b vs 14b) is config — locked once we know the GPU VRAM.
        self.model = model or os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")
        self.timeout = timeout

    def complete(self, system: str, user: str) -> str:
        resp = httpx.post(
            f"{self.url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "format": "json",          # force valid JSON (ADR 0016)
                "options": {"temperature": 0},  # deterministic, conservative
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Multi-turn chat with optional tool-calling (for the agent, ADR 0007).
        Returns the assistant message dict (may contain 'tool_calls')."""
        body: dict = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0},
        }
        if tools:
            body["tools"] = tools
        resp = httpx.post(f"{self.url}/api/chat", json=body, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()["message"]


class OpenAICompatClient:
    """Calls any OpenAI-compatible /chat/completions endpoint (Groq, OpenRouter,
    Together, …).

    DEV/TEST ONLY (ADR 0019). This is an *external* service — using it in the
    competition submission would violate the fully-local/offline requirement
    (spec §5.9, ADR 0009). It exists solely to unblock testing while the local
    GPU model server (ADR 0015) is being set up. `get_model()` never selects it
    unless `MODEL_PROVIDER` is set explicitly.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
        client: httpx.Client | None = None,
    ) -> None:
        # Default base points at Groq (free, fast, OpenAI-compatible, hosts
        # Qwen2.5 — the same family we run locally, so dev results are comparable).
        self.base_url = (
            base_url or os.environ.get("MODEL_API_BASE", "https://api.groq.com/openai/v1")
        ).rstrip("/")
        self.api_key = api_key if api_key is not None else os.environ.get("MODEL_API_KEY", "")
        if not self.api_key:
            raise RuntimeError(
                "OpenAICompatClient needs MODEL_API_KEY (external dev provider). "
                "Unset MODEL_PROVIDER to use the local Ollama model (ADR 0015/0019)."
            )
        # Reuse OLLAMA_MODEL as the fallback name so switching providers needs
        # no extra config; override with MODEL_NAME (e.g. a Groq model id).
        self.model = (
            model or os.environ.get("MODEL_NAME") or os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")
        )
        self.timeout = timeout
        # url/model attrs mirror OllamaClient so callers can log them uniformly.
        self.url = self.base_url
        self._client = client or httpx.Client(timeout=timeout)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def complete(self, system: str, user: str) -> str:
        resp = self._client.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},  # force valid JSON (ADR 0016)
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Multi-turn chat with optional tool-calling. Normalizes the OpenAI
        response to the same message dict shape OllamaClient returns, so the
        agent (ADR 0007) consumes both identically."""
        body: dict = {"model": self.model, "messages": messages, "temperature": 0}
        if tools:
            body["tools"] = tools
        resp = self._client.post(
            f"{self.base_url}/chat/completions", headers=self._headers(), json=body
        )
        resp.raise_for_status()
        msg = resp.json()["choices"][0]["message"]
        return {
            "role": msg.get("role", "assistant"),
            "content": msg.get("content") or "",
            "tool_calls": msg.get("tool_calls"),
        }


def get_model(timeout: float = 120.0) -> ChatModel:
    """Return the model client selected by `MODEL_PROVIDER` (default: ollama).

    - unset / 'ollama' / 'local' → `OllamaClient`: local, offline, on-prem. The
      ONLY provider valid for the competition submission (spec §5.9, ADR 0009).
    - 'groq' / 'openai' / 'api'  → `OpenAICompatClient`: external API, DEV/TEST
      ONLY (ADR 0019). Prints a loud warning; never use in the competition config.
    """
    provider = os.environ.get("MODEL_PROVIDER", "ollama").strip().lower()
    if provider in ("", "ollama", "local"):
        return OllamaClient(timeout=timeout)
    if provider in ("groq", "openai", "api", "openai-compat", "openrouter"):
        print(
            f"⚠️  Using an EXTERNAL model API (MODEL_PROVIDER={provider}). "
            "Dev/test only — the competition requires a fully local/offline model "
            "(spec §5.9, ADR 0009/0019). Do not use this in the submission.",
            file=sys.stderr,
        )
        return OpenAICompatClient(timeout=timeout)
    raise ValueError(
        f"Unknown MODEL_PROVIDER={provider!r}. Use 'ollama' (default) or 'groq'."
    )
