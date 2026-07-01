"""Control-panel operations (ADR 0018): run pipeline steps, read status, and
run read-only SQL. UI-free so it stays testable; the Streamlit app is app.py.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import httpx
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Pipeline steps the operator can trigger (the commands, behind buttons).
STEPS: dict[str, list[str]] = {
    "collection": ["uv", "run", "python", "scheduler/run_collection.py"],
    "extraction": ["uv", "run", "python", "-m", "banking_analysis.extraction.runner"],
    "validation": ["uv", "run", "python", "-m", "banking_analysis.validation.runner"],
    "eval": ["uv", "run", "python", "-m", "banking_analysis.extraction.eval"],
}

_WRITE_WORDS = ("insert", "update", "delete", "drop", "alter", "truncate",
                "create", "grant", "revoke", "comment", "copy", "merge")

_TABLE_QUERIES: dict[str, str] = {
    "banks": "SELECT * FROM banks ORDER BY id",
    "collection_runs": (
        "SELECT id, bank_id, url, ok, failure_reason, fetched_at, "
        "length(raw_text) AS chars FROM collection_runs ORDER BY id"
    ),
    "campaigns": "SELECT * FROM campaigns ORDER BY id",
    "campaign_fields": "SELECT * FROM campaign_fields ORDER BY id",
}


def _dsn() -> str:
    return os.environ.get(
        "DATABASE_URL", "postgresql://banking:banking@localhost:5432/banking_analysis"
    )


def run_step(name: str, timeout: float = 300.0) -> tuple[bool, str]:
    """Run a pipeline step as a subprocess; return (ok, combined output)."""
    cmd = STEPS[name]
    try:
        proc = subprocess.run(
            cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout:.0f}s"
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out.strip() or "(no output)"


def _query(sql: str, params: tuple = ()) -> tuple[list[str], list[tuple]]:
    with psycopg.connect(_dsn()) as conn:
        conn.read_only = True                 # DB-level guard (ADR 0017/0018)
        cur = conn.execute(sql, params)
        cols = [d.name for d in cur.description] if cur.description else []
        return cols, cur.fetchall()


def as_records(cols: list[str], rows: list[tuple]) -> list[dict]:
    return [dict(zip(cols, r)) for r in rows]


def status() -> dict:
    """Pipeline status snapshot. Returns {} if the DB is unreachable."""
    try:
        with psycopg.connect(_dsn()) as conn:
            conn.read_only = True
            g = lambda q: conn.execute(q).fetchone()[0]
            return {
                "banks": g("SELECT count(*) FROM banks"),
                # Current View (ADR 0017): distinct campaigns, not total runs.
                "collected": g("SELECT count(*) FROM (SELECT DISTINCT bank_id, url "
                               "FROM collection_runs WHERE ok) t"),
                "runs_total": g("SELECT count(*) FROM collection_runs"),  # full history
                "extracted": g("SELECT count(*) FROM campaigns"),
                "validated": g("SELECT count(*) FROM campaign_fields WHERE is_valid IS NOT NULL"),
                "scraped_banks": g("SELECT count(DISTINCT bank_id) FROM collection_runs WHERE ok"),
                "last_collection": g("SELECT max(fetched_at) FROM collection_runs WHERE ok"),
            }
    except Exception:
        return {}


def model_status() -> tuple[bool, str]:
    """Is the model server reachable, and what models does it have?"""
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    try:
        resp = httpx.get(f"{url}/api/tags", timeout=2.0)
        resp.raise_for_status()
        names = [m.get("name", "?") for m in resp.json().get("models", [])]
        return True, ", ".join(names) or "(no models pulled)"
    except Exception as exc:
        return False, f"unreachable at {url} ({type(exc).__name__})"


def browse_table(name: str) -> tuple[list[str], list[tuple]]:
    if name not in _TABLE_QUERIES:
        raise ValueError(f"unknown table {name}")
    return _query(_TABLE_QUERIES[name])


def table_names() -> list[str]:
    return list(_TABLE_QUERIES)


def read_only_sql(sql: str) -> tuple[list[str], list[tuple]]:
    """Run a user SELECT. Guarded twice: keyword check + read-only connection."""
    s = sql.strip().rstrip(";").strip()
    if not s:
        raise ValueError("Boş sorgu.")
    low = s.lower()
    if not (low.startswith("select") or low.startswith("with")):
        raise ValueError("Yalnızca SELECT sorgularına izin var (salt-okunur).")
    if any(re.search(rf"\b{w}\b", low) for w in _WRITE_WORDS):
        raise ValueError("Yazma/DDL anahtar kelimeleri engellendi (salt-okunur).")
    return _query(s)
