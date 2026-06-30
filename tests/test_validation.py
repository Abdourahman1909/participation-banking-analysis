"""Offline tests for Layer 3 validation (ADR 0008). No DB, no model.

    uv run python tests/test_validation.py
    uv run pytest tests/test_validation.py
"""

from __future__ import annotations

from banking_analysis.validation.normalize import parse_int, parse_number
from banking_analysis.validation.validator import validate_field


# ---- Turkish number parsing ----
def test_parse_decimal_comma():
    assert parse_number("%2,96") == 2.96

def test_parse_thousands_dot():
    assert parse_number("300.000 TL") == 300000.0

def test_parse_millions():
    assert parse_number("2.000.000 TL") == 2000000.0

def test_parse_mixed_sep():
    assert parse_number("1.234,56") == 1234.56

def test_parse_int_from_phrase():
    assert parse_int("12 ay") == 12

def test_parse_int_rejects_fraction():
    assert parse_int("12,5 ay") is None

def test_parse_none():
    assert parse_number("vade belirtilmemiştir") is None


# ---- field validation ----
def test_valid_grounded_in_range():
    r = validate_field("profit_share_rate", "%2,96", "aylık kâr payı oranı %2,96 olarak uygulanır")
    assert r.is_valid and r.normalized == 2.96

def test_value_not_in_quote_fails_substantiation():
    # quote says 2,96 but the value claims 3,96 — the model misread itself
    r = validate_field("profit_share_rate", "%3,96", "aylık kâr payı oranı %2,96 olarak uygulanır")
    assert not r.is_valid and "evidence" in r.reason

def test_rate_out_of_range():
    r = validate_field("profit_share_rate", "%296", "kâr payı oranı %296")
    assert not r.is_valid and "range" in r.reason

def test_maturity_valid():
    r = validate_field("maturity_months", "12", "vade 12 aydır")
    assert r.is_valid and r.normalized == 12

def test_maturity_out_of_range():
    r = validate_field("maturity_months", "1200", "vade 1200 ay")
    assert not r.is_valid and "range" in r.reason

def test_amount_valid():
    r = validate_field("cost_amount", "300.000 TL", "finansman tutarı 300.000 TL")
    assert r.is_valid and r.normalized == 300000.0

def test_null_value_not_validated():
    r = validate_field("cost_amount", None, None)
    assert r.is_valid and r.normalized is None


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
