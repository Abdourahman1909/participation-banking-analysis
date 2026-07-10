"""Response/request models for the HTTP contract (ADR 0022).

Field names are English like the DB schema; UI strings stay Turkish in the
frontend. The chat shapes reuse the agent's own models (ADR 0009) so the
contract can't drift from what the agent actually returns.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from banking_analysis.agent.models import Source


class Stats(BaseModel):
    banks: int | None = None
    campaigns: int | None = None          # Current View count (ADR 0017)
    last_collection: datetime | None = None
    db_ok: bool = True


class CampaignItem(BaseModel):
    bank: str
    title: str
    campaign_type: str
    profit_share_rate: str | None = None  # display string, as extracted
    maturity_months: str | None = None    # display string, as extracted
    cost_amount: str | None = None
    evidence_quote: str = ""              # ADR 0016 — never dropped
    rate_normalized: float | None = None  # value_normalized — sort on this
    term_months: int | None = None        # value_normalized — sort on this
    is_valid: bool = True


class CampaignList(BaseModel):
    items: list[CampaignItem]
    is_sample: bool                       # True → UI must badge as preview


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    is_preview: bool = False              # True → canned fallback answered


class PipelineStatus(BaseModel):
    db_ok: bool
    banks: int | None = None
    collected: int | None = None          # Current View
    runs_total: int | None = None         # full history
    extracted: int | None = None
    validated: int | None = None
    scraped_banks: int | None = None
    last_collection: datetime | None = None
    model_ok: bool = False
    model_detail: str = ""


class RunRequest(BaseModel):
    step: str                             # collection | extraction | validation


class RunStarted(BaseModel):
    run_id: int
    step: str


class RunInfo(BaseModel):
    id: int
    step: str
    started_at: datetime
    finished_at: datetime | None = None
    ok: bool | None = None                # None while running
