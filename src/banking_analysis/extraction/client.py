"""Layer 2 — model client (ADR 0005, 0015).

Talks to Ollama over HTTP. The model's *location* is config, not code
(`OLLAMA_URL`), so the model can live on a teammate's GPU laptop (ADR 0015)
while this code runs anywhere. The `ChatModel` Protocol lets the extractor be
tested with a fake model offline — no GPU needed (ADR 0016).
"""

from __future__ import annotations

import os
from typing import Protocol

import httpx


class ChatModel(Protocol):
    """Minimal interface the extractor needs. Real impl: OllamaClient.
    Tests pass a fake returning canned JSON."""

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
