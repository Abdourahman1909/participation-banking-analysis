"""Layer 2 — accuracy harness (ADR 0016): measure, don't assume.

A hand-built answer key over campaigns we actually scraped (the Kuveyt Türk
ones, whose text we read directly). When the model server is online, run:

    uv run python -m banking_analysis.extraction.eval

It extracts the real stored texts, compares to the key, and reports per-field
accuracy — so we know whether 7B is good enough or we need 14B / a tighter
prompt, instead of hoping. Comparison is lenient (digit-set match) because we
care whether the right number was found, not its exact string form.
"""

from __future__ import annotations

import re

from banking_analysis.extraction.client import get_model
from banking_analysis.extraction.extractor import extract_campaign
from banking_analysis.extraction.models import FIELD_NAMES
from banking_analysis.storage.db import connect

# Keyed by a unique slug in the campaign URL. None = the field should be null.
# Values hold the digits we expect the extracted value to contain.
GROUND_TRUTH: dict[str, dict] = {
    "yeni-musterilere-ozel-dijital-arac-finansmani": {
        "campaign_type": "vehicle_financing",
        "profit_share_rate": "2,96", "maturity_months": "12", "cost_amount": "300.000",
    },
    "civilde-vade-farksiz-4-aya-varan-taksit": {
        "campaign_type": "card",
        "profit_share_rate": None, "maturity_months": "4", "cost_amount": None,
    },
    "egitim-ve-saglik-harcamalarinizda-5-taksit": {
        "campaign_type": "card",
        "profit_share_rate": None, "maturity_months": "5", "cost_amount": None,
    },
    "babalar-gunu-hediyenize-1000-tl-nakit-iade": {
        "campaign_type": "new_customer",
        "profit_share_rate": None, "maturity_months": None, "cost_amount": "1.000",
    },
    "kampuse-gelenlere-toplamda-13500-tl-hediye": {
        "campaign_type": "new_customer",
        "profit_share_rate": None, "maturity_months": None, "cost_amount": "13.500",
    },
    "mobilden-kuveyt-turklu-olanlara-toplamda-7250-tl-hediye": {
        "campaign_type": "new_customer",
        "profit_share_rate": None, "maturity_months": None, "cost_amount": "7.250",
    },
}


def _digits(s: str | None) -> str:
    return re.sub(r"\D", "", s) if s else ""


def _field_correct(expected: str | None, got: str | None) -> bool:
    if expected is None:
        return got is None                       # correct null
    return got is not None and _digits(expected) in _digits(got)


def main() -> None:
    model = get_model()
    print(f"Model server: {model.url} ({model.model})\n")

    with connect() as conn:
        runs = conn.execute(
            "SELECT url, raw_text FROM collection_runs WHERE ok = TRUE"
        ).fetchall()

    total = correct = 0
    for slug, expected in GROUND_TRUTH.items():
        match = next(((u, t) for u, t in runs if slug in u), None)
        if not match:
            print(f"[skip] no scraped text for {slug}")
            continue
        url, raw_text = match
        try:
            result = extract_campaign(raw_text, model)
        except Exception as exc:
            print(f"[error] {slug}: {exc}")
            return

        type_ok = result.campaign_type == expected["campaign_type"]
        print(f"\n{slug}")
        print(f"  type: expected {expected['campaign_type']!r}, "
              f"got {result.campaign_type!r}  {'OK' if type_ok else 'MISS'}")
        total += 1
        correct += type_ok
        for name in FIELD_NAMES:
            exp = expected[name]
            got = result.fields[name].value if name in result.fields else None
            ok = _field_correct(exp, got)
            total += 1
            correct += ok
            print(f"  {name}: expected {exp!r}, got {got!r}  {'OK' if ok else 'MISS'}")

    if total:
        print(f"\nAccuracy: {correct}/{total} = {100 * correct / total:.0f}%")


if __name__ == "__main__":
    main()
