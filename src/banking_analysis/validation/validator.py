"""Layer 3 — the validator (ADR 0008).

Deterministic, rule-based, pass/fail — no LLM judge, no fuzzy score. For each
extracted field with a value it runs three checks and produces a typed
normalized value as a byproduct:

  1. Substantiation — the value's number actually appears in its evidence
     quote. (Extraction already proved the quote is in the source, ADR 0016;
     this catches the model misreading its own quote, e.g. value 3,96 vs a
     quote that says 2,96.)
  2. Parse/normalize — the string parses to a typed number (ADR 0017: stored
     in value_normalized; the original string is never overwritten).
  3. Range/format — the number is plausible for its field type.

Null-valued fields are not validated (nothing to check) — is_valid stays null.
"""

from __future__ import annotations

import re
from typing import Callable

from pydantic import BaseModel

from banking_analysis.validation.normalize import parse_int, parse_number


class FieldValidation(BaseModel):
    is_valid: bool
    reason: str | None = None
    normalized: float | None = None


def _in_range(lo: float, hi: float) -> Callable[[float], bool]:
    return lambda x: lo <= x <= hi


# field_name -> (parser, range predicate, human label for reasons)
_RULES: dict[str, tuple[Callable[[str | None], float | int | None], Callable[[float], bool], str]] = {
    # monthly profit share %, kept generous: catch garbage (296%, 0, negative)
    "profit_share_rate": (parse_number, lambda x: 0 < x <= 100, "kâr payı oranı"),
    # maturity in months: 1 month .. 40 years
    "maturity_months": (parse_int, _in_range(1, 480), "vade (ay)"),
    # monetary amount: positive, generous upper bound
    "cost_amount": (parse_number, lambda x: 0 < x <= 1e10, "tutar"),
}


def _digits(text: str | None) -> str:
    return re.sub(r"\D", "", text or "")


def _substantiated(value: str, quote: str | None) -> bool:
    """The value's digits appear in the quote's digits (separator-agnostic)."""
    v = _digits(value)
    return bool(v) and v in _digits(quote)


def validate_field(field_name: str, value: str | None, evidence_quote: str | None) -> FieldValidation:
    """Validate one extracted field. Caller skips null-value fields."""
    if value is None:
        return FieldValidation(is_valid=True, reason="no value to validate")

    rule = _RULES.get(field_name)
    if rule is None:
        return FieldValidation(is_valid=True, reason=f"no rule for {field_name}")
    parser, in_range, label = rule

    if not _substantiated(value, evidence_quote):
        return FieldValidation(is_valid=False, reason="value not supported by evidence quote")

    normalized = parser(value)
    if normalized is None:
        return FieldValidation(is_valid=False, reason=f"unparseable {label}: {value!r}")

    if not in_range(float(normalized)):
        return FieldValidation(
            is_valid=False, reason=f"{label} out of plausible range: {normalized}",
            normalized=float(normalized),
        )

    return FieldValidation(is_valid=True, normalized=float(normalized))
