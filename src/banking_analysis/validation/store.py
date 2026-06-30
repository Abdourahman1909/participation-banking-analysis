"""Layer 3 ↔ Layer 4 bridge: read extracted fields awaiting validation,
write back the verdict + normalized value (ADR 0008, 0017).
"""

from __future__ import annotations

import psycopg

from banking_analysis.validation.validator import FieldValidation


def pending_fields(conn: psycopg.Connection) -> list[tuple[int, str, str, str | None]]:
    """Fields with a value but no validation verdict yet, as
    (id, field_name, value, evidence_quote). Null-value fields are skipped —
    there's nothing to validate."""
    rows = conn.execute(
        """
        SELECT id, field_name, value, evidence_quote
        FROM campaign_fields
        WHERE value IS NOT NULL AND is_valid IS NULL
        ORDER BY id
        """
    ).fetchall()
    return [(r[0], r[1], r[2], r[3]) for r in rows]


def save_validation(conn: psycopg.Connection, field_id: int, result: FieldValidation) -> None:
    conn.execute(
        """
        UPDATE campaign_fields
        SET is_valid = %s, validation_reason = %s, value_normalized = %s
        WHERE id = %s
        """,
        (result.is_valid, result.reason, result.normalized, field_id),
    )
    conn.commit()
