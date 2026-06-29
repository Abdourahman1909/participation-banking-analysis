"""Thin Postgres access layer (ADR 0006: plain SQL, no ORM)."""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

import psycopg

from banking_analysis.collection.base import CollectionResult


def _dsn() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://banking:banking@localhost:5432/banking_analysis",
    )


@contextmanager
def connect() -> Iterator[psycopg.Connection]:
    with psycopg.connect(_dsn()) as conn:
        yield conn


def get_or_create_bank(conn: psycopg.Connection, name: str, website: str, is_digital: bool) -> int:
    row = conn.execute("SELECT id FROM banks WHERE name = %s", (name,)).fetchone()
    if row:
        return row[0]
    row = conn.execute(
        "INSERT INTO banks (name, website, is_digital) VALUES (%s, %s, %s) RETURNING id",
        (name, website, is_digital),
    ).fetchone()
    conn.commit()
    return row[0]


def save_collection_result(conn: psycopg.Connection, bank_id: int, result: CollectionResult) -> int:
    row = conn.execute(
        """
        INSERT INTO collection_runs (bank_id, url, fetched_at, ok, failure_reason, raw_text)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (bank_id, result.url, result.fetched_at, result.ok, result.failure_reason, result.text),
    ).fetchone()
    conn.commit()
    return row[0]


def latest_good_text(conn: psycopg.Connection, bank_id: int, url: str) -> str | None:
    """The Stale Bank Data lookup (CONTEXT.md): most recent ok=true text
    for this (bank, url), regardless of whether the very latest run failed.
    """
    row = conn.execute(
        """
        SELECT raw_text FROM collection_runs
        WHERE bank_id = %s AND url = %s AND ok = TRUE
        ORDER BY fetched_at DESC LIMIT 1
        """,
        (bank_id, url),
    ).fetchone()
    return row[0] if row else None
