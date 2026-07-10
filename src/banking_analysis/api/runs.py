"""Pipeline run execution + event store (ADR 0021/0022).

A run = one layer step executed as a background subprocess (same commands the
control panel uses, ADR 0018). Every output line is parsed into a structured
event (events.py) and appended to `pipeline_events`; the SSE endpoint streams
those rows. The stream is a live view of stored state — history survives
refreshes, and nothing is ever deleted (ADR 0017; only the run's finish
status is filled in at the end).

DB access is deliberately plain module functions so offline tests can patch
them with in-memory fakes.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Same commands as control_panel.ops.STEPS (minus eval — internal-only).
STEPS: dict[str, list[str]] = {
    "collection": [sys.executable, "-m", "banking_analysis.collection.runner"],
    "extraction": [sys.executable, "-m", "banking_analysis.extraction.runner"],
    "validation": [sys.executable, "-m", "banking_analysis.validation.runner"],
}

# Mirrored in db/schema.sql for fresh installs; IF NOT EXISTS makes this an
# idempotent migration for DBs created before ADR 0022.
DDL = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id          SERIAL PRIMARY KEY,
    step        TEXT NOT NULL,
    started_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    ok          BOOLEAN
);
CREATE TABLE IF NOT EXISTS pipeline_events (
    id          SERIAL PRIMARY KEY,
    run_id      INTEGER NOT NULL REFERENCES pipeline_runs(id),
    seq         INTEGER NOT NULL,
    event_type  TEXT NOT NULL,
    payload     JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_pipeline_events_run
    ON pipeline_events (run_id, seq);
"""


def _dsn() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://banking:banking@localhost:5432/banking_analysis",
    )


def ensure_tables() -> None:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        conn.execute(DDL)


# --- storage primitives (patched by offline tests) -------------------------

def insert_run(step: str) -> int:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        row = conn.execute(
            "INSERT INTO pipeline_runs (step) VALUES (%s) RETURNING id", (step,)
        ).fetchone()
    return row[0]


def finish_run(run_id: int, ok: bool) -> None:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        conn.execute(
            "UPDATE pipeline_runs SET finished_at = now(), ok = %s WHERE id = %s",
            (ok, run_id),
        )


def insert_event(conn, run_id: int, seq: int, event_type: str, payload: dict) -> None:
    conn.execute(
        "INSERT INTO pipeline_events (run_id, seq, event_type, payload) "
        "VALUES (%s, %s, %s, %s)",
        (run_id, seq, event_type, json.dumps(payload, ensure_ascii=False)),
    )


def event_conn():
    """One autocommit connection per run worker (events land immediately)."""
    return psycopg.connect(_dsn(), autocommit=True)


def fetch_events(run_id: int, after_seq: int = 0) -> list[dict]:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        rows = conn.execute(
            "SELECT seq, event_type, payload, created_at FROM pipeline_events "
            "WHERE run_id = %s AND seq > %s ORDER BY seq",
            (run_id, after_seq),
        ).fetchall()
    return [
        {"seq": r[0], "event_type": r[1], "payload": r[2], "at": r[3]}
        for r in rows
    ]


def fetch_runs(limit: int = 20) -> list[dict]:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        rows = conn.execute(
            "SELECT id, step, started_at, finished_at, ok FROM pipeline_runs "
            "ORDER BY id DESC LIMIT %s",
            (limit,),
        ).fetchall()
    return [
        {"id": r[0], "step": r[1], "started_at": r[2],
         "finished_at": r[3], "ok": r[4]}
        for r in rows
    ]


def run_finished(run_id: int) -> bool:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        row = conn.execute(
            "SELECT finished_at IS NOT NULL FROM pipeline_runs WHERE id = %s",
            (run_id,),
        ).fetchone()
    return bool(row and row[0])


# --- run manager ------------------------------------------------------------

class StepBusy(Exception):
    """The step already has a live run — one at a time (ADR 0022)."""


class RunManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._threads: dict[str, threading.Thread] = {}

    def start(self, step: str) -> int:
        if step not in STEPS:
            raise KeyError(step)
        with self._lock:
            t = self._threads.get(step)
            if t is not None and t.is_alive():
                raise StepBusy(step)
            run_id = insert_run(step)
            t = threading.Thread(
                target=self._worker, args=(run_id, step), daemon=True,
                name=f"pipeline-{step}-{run_id}",
            )
            self._threads[step] = t
            t.start()
        return run_id

    def _worker(self, run_id: int, step: str) -> None:
        from banking_analysis.api.events import parse_line

        seq = 0
        ok = False
        with event_conn() as conn:
            def emit(event_type: str, payload: dict) -> None:
                nonlocal seq
                seq += 1
                insert_event(conn, run_id, seq, event_type, payload)

            emit("step_started", {"step": step})
            try:
                proc = subprocess.Popen(
                    STEPS[step], cwd=PROJECT_ROOT,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, errors="replace",
                )
                assert proc.stdout is not None
                for raw in proc.stdout:
                    parsed = parse_line(raw)
                    if parsed:
                        emit(*parsed)
                ok = proc.wait() == 0
            except Exception as exc:  # subprocess couldn't run at all
                emit("log", {"line": f"runner error: {exc}", "level": "error"})
            emit("step_done", {"step": step, "ok": ok})
        finish_run(run_id, ok)


MANAGER = RunManager()
