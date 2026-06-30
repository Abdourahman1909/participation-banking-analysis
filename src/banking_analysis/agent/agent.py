"""Layer 5 — the tool-calling agent (ADR 0007, 0009).

The model decides which tools to call; this code runs them (read-only) and
feeds the results back. Sources are attached deterministically from the tool
results actually used — the model can't cite something it didn't retrieve.
"""

from __future__ import annotations

import json
from typing import Protocol

import psycopg

from banking_analysis.agent.models import AgentAnswer, Source
from banking_analysis.agent.prompt import SYSTEM_PROMPT
from banking_analysis.agent.tools import TOOL_FUNCS, TOOL_SCHEMAS


class ChatModel(Protocol):
    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict: ...


def _tool_args(call: dict) -> tuple[str, dict]:
    fn = call.get("function", call)
    name = fn.get("name", "")
    args = fn.get("arguments", {})
    if isinstance(args, str):              # some backends return a JSON string
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}
    return name, args or {}


def _sources_from(rows: list[dict]) -> list[Source]:
    out: list[Source] = []
    seen: set = set()
    for r in rows:
        key = (r.get("bank"), r.get("title"))
        if key in seen:
            continue
        seen.add(key)
        out.append(Source(
            bank=r.get("bank", "?"), title=r.get("title"),
            field="profit_share_rate" if r.get("profit_share_rate") else None,
            value=r.get("profit_share_rate"), evidence_quote=r.get("rate_evidence"),
        ))
    return out


def answer(question: str, model: ChatModel, conn: psycopg.Connection,
           max_rounds: int = 3) -> AgentAnswer:
    """Answer one question. Read-only: the agent can only query, never write."""
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    collected: list[dict] = []

    for _ in range(max_rounds):
        try:
            msg = model.chat(messages, tools=TOOL_SCHEMAS)
        except Exception as exc:
            return AgentAnswer(answer=f"Şu an yanıt veremedim ({exc}).", in_scope=True)

        calls = msg.get("tool_calls")
        if not calls:
            # Final answer (or an off-topic decline → no tools were used).
            return AgentAnswer(
                answer=msg.get("content", "").strip() or
                       "Bu konuda yardımcı olamadım.",
                sources=_sources_from(collected),
                in_scope=bool(collected),
            )

        messages.append(msg)
        for call in calls:
            name, args = _tool_args(call)
            fn = TOOL_FUNCS.get(name)
            result = fn(conn, **args) if fn else {"error": f"unknown tool {name}"}
            if isinstance(result, list):
                collected.extend(result)
            messages.append({"role": "tool", "content": json.dumps(result, ensure_ascii=False)})

    # Ran out of rounds — answer from what we have.
    return AgentAnswer(
        answer="İsteğinizi tam çözümleyemedim, ancak ilgili kampanyaları aşağıda bulabilirsiniz.",
        sources=_sources_from(collected), in_scope=bool(collected),
    )
