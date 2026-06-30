"""Offline proof of the verify-don't-trust logic (ADR 0016).

No model / no GPU needed: a FakeModel returns canned JSON (including
hallucinations), and we assert the extractor catches them. Run either way:

    uv run python tests/test_extraction.py      # plain runner
    uv run pytest tests/test_extraction.py       # if pytest is installed
"""

from __future__ import annotations

import json

from banking_analysis.extraction.extractor import extract_campaign

# Source text the model is "reading". Quotes must match THIS to be grounded.
SOURCE = (
    "Kampanya kapsamında aylık kâr payı oranı %2,96 olarak uygulanır. "
    "Vade 12 aydır. Detaylar için şubelerimize başvurun."
)


class FakeModel:
    """Returns a fixed payload, ignoring the prompt — stands in for Ollama."""

    def __init__(self, payload: str) -> None:
        self.payload = payload

    def complete(self, system: str, user: str) -> str:
        return self.payload


def _payload(**fields) -> str:
    base = {
        "is_campaign": True,
        "title": "Test",
        "campaign_type": "vehicle_financing",
        "profit_share_rate": {"value": None, "evidence_quote": None},
        "maturity_months": {"value": None, "evidence_quote": None},
        "cost_amount": {"value": None, "evidence_quote": None},
    }
    base.update(fields)
    return json.dumps(base, ensure_ascii=False)


def test_grounded_value_is_kept():
    p = _payload(profit_share_rate={
        "value": "%2,96",
        "evidence_quote": "aylık kâr payı oranı %2,96 olarak uygulanır",
    })
    r = extract_campaign(SOURCE, FakeModel(p))
    assert r.ok and not r.is_no_campaign
    assert r.fields["profit_share_rate"].value == "%2,96"
    assert not r.fields["profit_share_rate"].dropped


def test_hallucinated_quote_is_dropped():
    # Model invents a rate and a supporting sentence that is NOT in the source.
    p = _payload(profit_share_rate={
        "value": "%9,99",
        "evidence_quote": "aylık kâr payı oranı %9,99 olarak uygulanır",
    })
    r = extract_campaign(SOURCE, FakeModel(p))
    f = r.fields["profit_share_rate"]
    assert f.value is None and f.dropped
    assert any("profit_share_rate" in d for d in r.diagnostics)


def test_value_without_quote_is_dropped():
    p = _payload(maturity_months={"value": "12", "evidence_quote": None})
    r = extract_campaign(SOURCE, FakeModel(p))
    assert r.fields["maturity_months"].value is None
    assert r.fields["maturity_months"].dropped


def test_legitimate_null_is_kept_not_flagged():
    r = extract_campaign(SOURCE, FakeModel(_payload()))
    f = r.fields["cost_amount"]
    assert f.value is None and not f.dropped


def test_no_campaign_detected():
    r = extract_campaign(SOURCE, FakeModel(_payload(is_campaign=False)))
    assert r.ok and r.is_no_campaign


def test_malformed_output_is_a_failure():
    r = extract_campaign(SOURCE, FakeModel("this is not json"))
    assert not r.ok and r.failure_reason


def test_unknown_campaign_type_folds_to_other():
    r = extract_campaign(SOURCE, FakeModel(_payload(campaign_type="süper_kampanya")))
    assert r.campaign_type == "other"


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
