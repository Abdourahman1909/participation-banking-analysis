"""Layer 2 — Extraction data models (ADR 0004, 0011, 0014, 0016).

The model's raw output is parsed leniently into ``RawCampaign`` (defaults
everywhere, so missing keys don't crash). The extractor then verifies it and
produces an ``ExtractionResult`` — the trusted, grounded output.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# campaign_type enum from db/schema.sql (ADR 0011). Closed set; "other" is the
# catch-all an unknown model value is folded into.
CAMPAIGN_TYPES: tuple[str, ...] = (
    "funding",
    "personal_financing",
    "housing_finance",
    "vehicle_financing",
    "card",
    "shopping_points",
    "new_customer",
    "investment_product",
    "other",
)

# The financial fields we extract per campaign (campaign_fields.field_name).
FIELD_NAMES: tuple[str, ...] = (
    "profit_share_rate",   # kâr payı oranı
    "maturity_months",     # vade (ay)
    "cost_amount",         # tutar / maliyet
)


class RawField(BaseModel):
    """One {value, evidence_quote} pair as the model returned it."""

    value: str | None = None
    evidence_quote: str | None = None


class RawCampaign(BaseModel):
    """The model's raw JSON, parsed leniently. Nothing here is trusted yet."""

    is_campaign: bool = True
    title: str | None = None
    campaign_type: str | None = None
    profit_share_rate: RawField = Field(default_factory=RawField)
    maturity_months: RawField = Field(default_factory=RawField)
    cost_amount: RawField = Field(default_factory=RawField)


class VerifiedField(BaseModel):
    """A field after the grounding gate. ``value``/``evidence_quote`` are both
    None when the model didn't state it OR when its quote failed verification
    (the two are distinguished by ``dropped``)."""

    value: str | None = None
    evidence_quote: str | None = None
    dropped: bool = False          # True = model gave a value but we rejected it
    drop_reason: str | None = None


class ExtractionResult(BaseModel):
    """The trusted output of extracting one source text."""

    ok: bool                       # did we get a usable, parseable response
    is_no_campaign: bool = False   # ADR 0014 — text processed, but not a campaign
    title: str | None = None
    campaign_type: str | None = None
    fields: dict[str, VerifiedField] = Field(default_factory=dict)
    diagnostics: list[str] = Field(default_factory=list)
    failure_reason: str | None = None   # set when ok is False
