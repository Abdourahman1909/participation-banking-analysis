"""Layer 3 — normalization (ADR 0008).

Turn as-extracted Turkish strings into typed, comparable numbers. Turkish
convention: '.' is the thousands separator, ',' is the decimal — so
"2.000.000" is two million and "2,96" is two-point-nine-six. Returns None
when there's no parseable number (validation then marks the field invalid).
"""

from __future__ import annotations

import re

_NUM = re.compile(r"\d[\d.,]*")


def parse_number(text: str | None) -> float | None:
    """First numeric token in the string, read with Turkish separators.
    "%2,96" -> 2.96 ; "300.000 TL" -> 300000.0 ; "1.234,56" -> 1234.56"""
    if not text:
        return None
    m = _NUM.search(text)
    if not m:
        return None
    token = m.group(0).rstrip(".,")
    token = token.replace(".", "").replace(",", ".")  # '.' thousands, ',' decimal
    try:
        return float(token)
    except ValueError:
        return None


def parse_int(text: str | None) -> int | None:
    """Whole-number fields like maturity months. "12 ay" -> 12. A non-whole
    number (e.g. "12,5 ay") is rejected as None — implausible for a maturity."""
    n = parse_number(text)
    if n is None or n != int(n):
        return None
    return int(n)
