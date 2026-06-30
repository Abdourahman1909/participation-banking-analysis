"""Layer 2 — the extractor (ADR 0004, 0011, 0014, 0016).

Turns one source text into a trusted ExtractionResult. The model proposes;
this code verifies. The key gate: every value must be backed by an
evidence_quote that actually appears in the source text, or it is dropped.
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from banking_analysis.extraction.client import ChatModel
from banking_analysis.extraction.models import (
    CAMPAIGN_TYPES,
    FIELD_NAMES,
    ExtractionResult,
    RawCampaign,
    RawField,
    VerifiedField,
)
from banking_analysis.extraction.prompt import SYSTEM_PROMPT, build_user_prompt


def _norm(text: str) -> str:
    """Normalize for substring comparison: collapse whitespace, casefold.
    Errs toward false-negatives (a real quote might fail) over false-
    positives — dropping a real value is the safe failure mode (ADR 0016)."""
    return " ".join(text.split()).casefold()


def _is_grounded(quote: str | None, source_norm: str) -> bool:
    if not quote or not quote.strip():
        return False
    return _norm(quote) in source_norm


def _coerce_type(raw_type: str | None) -> str | None:
    """Closed enum (ADR 0011): unknown non-null values fold to 'other'."""
    if raw_type is None:
        return None
    return raw_type if raw_type in CAMPAIGN_TYPES else "other"


def _verify_field(raw: RawField, source_norm: str) -> tuple[VerifiedField, str | None]:
    """Apply the grounding gate to one field. Returns (field, diagnostic)."""
    if raw.value is None:
        return VerifiedField(value=None, evidence_quote=None), None  # legit null
    if not _is_grounded(raw.evidence_quote, source_norm):
        reason = (
            "no evidence quote" if not raw.evidence_quote
            else "evidence quote not found in source"
        )
        return (
            VerifiedField(value=None, evidence_quote=None, dropped=True, drop_reason=reason),
            f"dropped value {raw.value!r}: {reason}",
        )
    return VerifiedField(value=raw.value, evidence_quote=raw.evidence_quote), None


def extract_campaign(source_text: str, model: ChatModel) -> ExtractionResult:
    """Extract + verify one campaign text. Never raises for model/parse
    problems — they become ok=False results so a batch run can continue."""
    try:
        content = model.complete(SYSTEM_PROMPT, build_user_prompt(source_text))
    except Exception as exc:  # network/timeout/etc — a failed extraction, not a crash
        return ExtractionResult(ok=False, failure_reason=f"model call failed: {exc}")

    try:
        raw = RawCampaign.model_validate(json.loads(content))
    except (json.JSONDecodeError, ValidationError) as exc:
        return ExtractionResult(ok=False, failure_reason=f"unparseable output: {exc}")

    if not raw.is_campaign:
        return ExtractionResult(ok=True, is_no_campaign=True)

    source_norm = _norm(source_text)
    fields: dict[str, VerifiedField] = {}
    diagnostics: list[str] = []
    for name in FIELD_NAMES:
        verified, note = _verify_field(getattr(raw, name), source_norm)
        fields[name] = verified
        if note:
            diagnostics.append(f"{name}: {note}")

    return ExtractionResult(
        ok=True,
        is_no_campaign=False,
        title=raw.title,
        campaign_type=_coerce_type(raw.campaign_type),
        fields=fields,
        diagnostics=diagnostics,
    )
