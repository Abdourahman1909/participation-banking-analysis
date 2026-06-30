"""Offline tests for Layer 5 agent (ADR 0007, 0009). No model, no real DB.

A FakeModel scripts the tool-call protocol; a FakeConn returns canned rows.

    uv run python tests/test_agent.py
    uv run pytest tests/test_agent.py
"""

from __future__ import annotations

from banking_analysis.agent.agent import answer

# campaigns row shape from tools._BASE_QUERY:
# (bank, title, type, rate_value, rate_norm, rate_evidence, maturity, amount)
_ROWS = [
    ("Türkiye Finans", "Taşıt Avantajı", "vehicle_financing",
     "%2,89", 2.89, "Taşıt finansmanında aylık kâr payı %2,89.", "12", "250.000 TL"),
    ("Kuveyt Türk", "Dijital Araç", "vehicle_financing",
     "%2,96", 2.96, "12 ay, aylık kâr oranı %2,96.", "12", "300.000 TL"),
]


class FakeResult:
    def __init__(self, rows): self._rows = rows
    def fetchall(self): return self._rows


class FakeConn:
    def __init__(self, rows): self.rows = rows
    def execute(self, sql, params=()): return FakeResult(self.rows)


class FakeModel:
    """Returns the scripted assistant messages in order."""
    def __init__(self, scripted): self.scripted = list(scripted); self.i = 0
    def chat(self, messages, tools=None):
        msg = self.scripted[self.i]; self.i += 1; return msg


def _tool_call(name, **args):
    return {"role": "assistant", "content": "",
            "tool_calls": [{"function": {"name": name, "arguments": args}}]}


def test_recommendation_is_grounded_with_sources():
    model = FakeModel([
        _tool_call("compare_by_rate", campaign_type="vehicle_financing"),
        {"role": "assistant",
         "content": "En uygun taşıt finansmanı Türkiye Finans'ta: aylık %2,89."},
    ])
    res = answer("en uygun taşıt finansmanı hangi bankada?", model, FakeConn(_ROWS))
    assert "Türkiye Finans" in res.answer
    assert res.in_scope and res.sources
    assert res.sources[0].bank == "Türkiye Finans"
    assert res.sources[0].evidence_quote                       # carries the proof


def test_off_topic_is_declined_without_sources():
    # Model uses no tool and declines (per the scope-guard prompt).
    model = FakeModel([
        {"role": "assistant",
         "content": "Yalnızca katılım bankası kampanyaları hakkında yardımcı olabilirim."},
    ])
    res = answer("write me a python script", model, FakeConn(_ROWS))
    assert not res.sources and not res.in_scope
    assert "katılım" in res.answer.lower()


def test_no_data_yields_no_invented_sources():
    model = FakeModel([
        _tool_call("get_campaigns", campaign_type="housing_finance"),
        {"role": "assistant", "content": "Şu an bu konuda veri bulunmuyor."},
    ])
    res = answer("konut finansmanı kampanyaları neler?", model, FakeConn([]))
    assert res.sources == []                                   # nothing invented


def _run_all() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t(); print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL  {t.__name__}  {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed


if __name__ == "__main__":
    raise SystemExit(_run_all())
