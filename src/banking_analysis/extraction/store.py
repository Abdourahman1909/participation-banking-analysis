"""Layer 2 ↔ Layer 4 bridge: read raw text from collection_runs, write
verified extractions into campaigns / campaign_fields (ADR 0006, 0014, 0016).

is_valid / validation_reason are left NULL here — that's the validation
layer's job (ADR 0008, Layer 3). Extraction only guarantees groundedness.
"""

from __future__ import annotations

import psycopg

from banking_analysis.extraction.models import FIELD_NAMES, ExtractionResult


def pending_runs(conn: psycopg.Connection) -> list[tuple[int, int, str, str]]:
    """The Current View of collection to extract (ADR 0017): the *latest*
    known-good snapshot per (bank, url) that hasn't been extracted yet, as
    (run_id, bank_id, url, raw_text). Older snapshots stay as raw history but
    aren't re-extracted, so campaigns don't double-count re-scrapes."""
    rows = conn.execute(
        """
        SELECT latest.id, latest.bank_id, latest.url, latest.raw_text
        FROM (
            SELECT DISTINCT ON (cr.bank_id, cr.url)
                   cr.id, cr.bank_id, cr.url, cr.raw_text
            FROM collection_runs cr
            WHERE cr.ok = TRUE AND cr.raw_text IS NOT NULL
            ORDER BY cr.bank_id, cr.url, cr.fetched_at DESC
        ) latest
        WHERE NOT EXISTS (
            SELECT 1 FROM campaigns c WHERE c.collection_run_id = latest.id
        )
        ORDER BY latest.id
        """
    ).fetchall()
    return [(r[0], r[1], r[2], r[3]) for r in rows]


def save_result(
    conn: psycopg.Connection,
    run_id: int,
    bank_id: int,
    url: str,
    result: ExtractionResult,
) -> int:
    """Persist one ExtractionResult. Writes a campaigns row and one
    campaign_fields row per field (null where not stated/dropped, so we know
    it was considered — ADR 0014). Returns the new campaign id."""
    campaign_id = conn.execute(
        """
        INSERT INTO campaigns
            (bank_id, collection_run_id, source_url, campaign_type, title, is_no_campaign)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (bank_id, run_id, url, result.campaign_type, result.title, result.is_no_campaign),
    ).fetchone()[0]

    if not result.is_no_campaign:
        for name in FIELD_NAMES:
            field = result.fields.get(name)
            conn.execute(
                """
                INSERT INTO campaign_fields (campaign_id, field_name, value, evidence_quote)
                VALUES (%s, %s, %s, %s)
                """,
                (campaign_id, name, field.value if field else None,
                 field.evidence_quote if field else None),
            )
    conn.commit()
    return campaign_id
