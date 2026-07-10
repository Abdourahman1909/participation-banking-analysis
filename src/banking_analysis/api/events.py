"""Log-line → structured event parsing (ADR 0022).

The layer runners keep printing their normal logging output; this adapter
parses those lines into the structured events the monitor UI renders as a
clean timeline (ADR 0021 — the polished replacement for raw terminal logs).
Parsing lives HERE, not in the layers, so no layer code changes. Any line
that matches nothing becomes a raw `log` event — nothing is dropped.
"""

from __future__ import annotations

import re

# `logging.basicConfig` default line format is  LEVEL:logger:message
_LOG_PREFIX = re.compile(r"^(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL):[\w.]*:")

# Ordered — first match wins, most specific first.
_PATTERNS: list[tuple[str, re.Pattern]] = [
    # collection: "Kuveyt Türk: 10/10 campaigns collected"
    ("bank_done", re.compile(
        r"^(?P<bank>.+?): (?P<collected>\d+)/(?P<total>\d+) campaigns collected")),
    # collection: "T.O.M. FAILED: https://… — reason"
    ("bank_failed", re.compile(
        r"^(?P<bank>.+?) FAILED: (?P<url>https?://\S+) — (?P<reason>.*)")),
    # scrapling: "[ts] INFO: Fetched (200) <GET https://…> (referer: …)"
    ("page_fetched", re.compile(
        r"Fetched \((?P<status>\d+)\)(?: <GET (?P<url>[^>]+)>)?")),
    # extraction: "run 12 FAILED: reason"
    ("extract_failed", re.compile(
        r"^run (?P<run>\d+) FAILED: (?P<reason>.*)")),
    # extraction: "run 12 — dropped profit_share_rate: quote not in source"
    ("field_dropped", re.compile(
        r"^run (?P<run>\d+) — (?P<detail>.*)")),
    # extraction: "13 collection run(s) pending extraction"
    ("pending", re.compile(
        r"^(?P<count>\d+) collection run\(s\) pending extraction")),
    # validation: "37 field(s) pending validation"
    ("pending", re.compile(
        r"^(?P<count>\d+) field\(s\) pending validation")),
    # validation: "field 8 (profit_share_rate='%2,96') INVALID: reason"
    ("field_invalid", re.compile(
        r"^field (?P<field_id>\d+) \((?P<field>[^)]*)\) INVALID: (?P<reason>.*)")),
    # extraction/validation: "done: …" summary lines
    ("summary", re.compile(r"^done: (?P<detail>.*)")),
    # extraction: "model server: http://… (qwen2.5:7b-instruct)"
    ("model_info", re.compile(r"^model server: (?P<detail>.*)")),
]

_WARN_TYPES = {"bank_failed", "extract_failed", "field_invalid"}


def parse_line(raw: str) -> tuple[str, dict] | None:
    """One output line → (event_type, payload), or None for a blank line."""
    line = raw.rstrip()
    if not line.strip():
        return None

    level = "info"
    m = _LOG_PREFIX.match(line)
    if m:
        level = m.group("level").lower()
        line = line[m.end():].strip()

    for event_type, pattern in _PATTERNS:
        m = pattern.search(line)
        if m:
            payload = {k: v for k, v in m.groupdict().items() if v is not None}
            for key in ("collected", "total", "count", "status", "run", "field_id"):
                if key in payload:
                    payload[key] = int(payload[key])
            if event_type in _WARN_TYPES:
                payload["level"] = "warning"
            return event_type, payload

    # Unparsed line — keep it (append-only honesty), rendered muted in the UI.
    return "log", {"line": line, "level": level}
