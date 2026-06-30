"""Layer 3 — batch validation entry point (ADR 0008).

Validates every extracted field that doesn't have a verdict yet. Pure SQL +
deterministic rules; no model, so it runs anywhere (no GPU needed). Run after
extraction:

    uv run python -m banking_analysis.validation.runner
"""

from __future__ import annotations

import logging

from banking_analysis.storage.db import connect
from banking_analysis.validation.store import pending_fields, save_validation
from banking_analysis.validation.validator import validate_field

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("validation_run")


def main() -> None:
    with connect() as conn:
        fields = pending_fields(conn)
        log.info("%d field(s) pending validation", len(fields))

        passed = failed = 0
        for field_id, name, value, quote in fields:
            result = validate_field(name, value, quote)
            save_validation(conn, field_id, result)
            if result.is_valid:
                passed += 1
            else:
                failed += 1
                log.info("field %d (%s=%r) INVALID: %s", field_id, name, value, result.reason)

        log.info("done: %d valid, %d invalid", passed, failed)


if __name__ == "__main__":
    main()
