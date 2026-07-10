"""Offline tests for the HTTP API boundary (ADR 0022). No DB, no model, no
network: storage access is patched to fail (proving the graceful sample-data
degradation), and pipeline runs execute a scripted subprocess whose events
land in an in-memory store.

    uv run python tests/test_api.py
    uv run pytest tests/test_api.py
"""

from __future__ import annotations

import sys
import time
from contextlib import contextmanager

from fastapi.testclient import TestClient

import banking_analysis.storage.db as storage_db
from banking_analysis.api import runs
from banking_analysis.api.events import parse_line

# Never touch a real DB from tests, even if one is running.
runs.ensure_tables = lambda: None

from banking_analysis.api.app import app  # noqa: E402  (after the patch)

client = TestClient(app)


@contextmanager
def _db_down():
    """Make storage.db.connect fail like an unreachable Postgres."""
    original = storage_db.connect

    @contextmanager
    def refused():
        raise ConnectionError("connection refused (test)")
        yield  # pragma: no cover

    storage_db.connect = refused
    try:
        yield
    finally:
        storage_db.connect = original


# --- event parsing -----------------------------------------------------------

def test_parse_collection_lines():
    t, p = parse_line("INFO:collection_run:Kuveyt Türk: 10/10 campaigns collected")
    assert t == "bank_done" and p == {"bank": "Kuveyt Türk", "collected": 10, "total": 10}

    t, p = parse_line("WARNING:collection_run:T.O.M. FAILED: https://x.tr/a — timeout")
    assert t == "bank_failed" and p["bank"] == "T.O.M." and p["level"] == "warning"

    t, p = parse_line("[2026-07-10 19:23:30] INFO: Fetched (200) "
                      "<GET https://x.tr/kampanya> (referer: https://www.google.com/)")
    assert t == "page_fetched" and p["status"] == 200
    assert p["url"] == "https://x.tr/kampanya"


def test_parse_extraction_and_validation_lines():
    t, p = parse_line("INFO:extraction_run:13 collection run(s) pending extraction")
    assert t == "pending" and p["count"] == 13

    t, p = parse_line("WARNING:extraction_run:run 7 FAILED: model unreachable")
    assert t == "extract_failed" and p["run"] == 7

    t, p = parse_line("INFO:extraction_run:run 7 — dropped profit_share_rate: quote not in source")
    assert t == "field_dropped" and "dropped" in p["detail"]

    t, p = parse_line("INFO:validation_run:field 8 (profit_share_rate='%2,96') INVALID: not in quote")
    assert t == "field_invalid" and p["field_id"] == 8

    t, p = parse_line("INFO:validation_run:done: 30 valid, 2 invalid")
    assert t == "summary"


def test_parse_unknown_line_kept_as_log():
    t, p = parse_line("some completely unexpected output")
    assert t == "log" and p["line"].startswith("some completely")
    assert parse_line("   \n") is None                       # blanks dropped


# --- data endpoints degrade to sample when the DB is down ---------------------

def test_stats_reports_db_down():
    with _db_down():
        r = client.get("/api/stats")
    assert r.status_code == 200 and r.json()["db_ok"] is False


def test_campaigns_fall_back_to_sample_with_evidence():
    with _db_down():
        r = client.get("/api/campaigns")
    body = r.json()
    assert body["is_sample"] is True and len(body["items"]) > 0
    assert all(i["evidence_quote"] for i in body["items"])   # ADR 0016 survives

    with _db_down():
        r = client.get("/api/campaigns", params={"type": "vehicle_financing"})
    assert {i["campaign_type"] for i in r.json()["items"]} == {"vehicle_financing"}


def test_chat_canned_fallback_keeps_answer_plus_sources_contract():
    with _db_down():
        r = client.post("/api/chat", json={"question": "en uygun konut finansmanı?"})
    body = r.json()
    assert body["is_preview"] is True and body["answer"]
    assert body["sources"] and body["sources"][0]["evidence_quote"]  # ADR 0009


# --- pipeline runs against an in-memory store ---------------------------------

class _MemStore:
    """Patches runs.py's storage primitives; events land in a list."""

    def __init__(self):
        self.events: list[tuple[str, dict]] = []
        self.finished: tuple[int, bool] | None = None
        self._saved = {}

    class _Conn:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def __enter__(self):
        self._saved = {n: getattr(runs, n) for n in
                       ("insert_run", "finish_run", "event_conn", "insert_event")}
        runs.insert_run = lambda step: 1
        runs.finish_run = lambda rid, ok: setattr(self, "finished", (rid, ok))
        runs.event_conn = lambda: self._Conn()
        runs.insert_event = (
            lambda conn, rid, seq, etype, payload: self.events.append((etype, payload)))
        return self

    def __exit__(self, *a):
        for n, f in self._saved.items():
            setattr(runs, n, f)
        return False


_SCRIPT = (
    "import sys;"
    "print('INFO:collection_run:Kuveyt Türk: 10/10 campaigns collected');"
    "print('unstructured noise');"
    "sys.exit(0)"
)


def test_run_manager_emits_structured_events():
    with _MemStore() as store:
        saved = runs.STEPS["collection"]
        runs.STEPS["collection"] = [sys.executable, "-c", _SCRIPT]
        try:
            manager = runs.RunManager()
            manager.start("collection")
            manager._threads["collection"].join(timeout=30)
        finally:
            runs.STEPS["collection"] = saved

    types = [t for t, _ in store.events]
    assert types[0] == "step_started" and types[-1] == "step_done"
    assert "bank_done" in types and "log" in types           # parsed + raw kept
    assert store.events[-1][1]["ok"] is True
    assert store.finished == (1, True)


def test_run_manager_rejects_concurrent_same_step():
    with _MemStore():
        saved = runs.STEPS["collection"]
        runs.STEPS["collection"] = [sys.executable, "-c", "import time; time.sleep(2)"]
        try:
            manager = runs.RunManager()
            manager.start("collection")
            time.sleep(0.2)
            try:
                manager.start("collection")
                assert False, "second start should raise StepBusy"
            except runs.StepBusy:
                pass
        finally:
            runs.STEPS["collection"] = saved
            manager._threads["collection"].join(timeout=30)


def test_run_endpoint_rejects_unknown_step():
    r = client.post("/api/pipeline/run", json={"step": "rm-rf"})
    assert r.status_code == 422


def test_sse_stream_replays_events_then_ends():
    saved_fetch, saved_done = runs.fetch_events, runs.run_finished
    calls = {"n": 0}

    def fake_fetch(run_id, after_seq=0):
        calls["n"] += 1
        if calls["n"] == 1:
            return [{"seq": 1, "event_type": "step_started", "payload": {"step": "collection"}},
                    {"seq": 2, "event_type": "bank_done",
                     "payload": {"bank": "Kuveyt Türk", "collected": 10, "total": 10}}]
        return []

    runs.fetch_events = fake_fetch
    runs.run_finished = lambda run_id: True
    try:
        r = client.get("/api/pipeline/runs/1/events")
    finally:
        runs.fetch_events, runs.run_finished = saved_fetch, saved_done

    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    assert '"type": "bank_done"' in r.text and "Kuveyt Türk" in r.text
    assert "event: end" in r.text


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
