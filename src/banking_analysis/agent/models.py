"""Layer 5 — agent answer types (ADR 0007, 0009).

The answer + sources contract: every answer carries the sources it was built
from. Sources are attached deterministically from the tool results the agent
actually used — not from the model claiming a citation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Source(BaseModel):
    """One cited campaign behind an answer."""

    bank: str
    title: str | None = None
    field: str | None = None          # e.g. "profit_share_rate"
    value: str | None = None
    evidence_quote: str | None = None


class AgentAnswer(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    in_scope: bool = True             # False when the question was declined/redirected
