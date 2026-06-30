"""Layer 2 — batch extraction entry point (ADR 0003, 0016).

Processes every not-yet-extracted collection_run through the model + grounding
gate and stores the verified result. Run after collection, on the machine
that can reach the model server (OLLAMA_URL → the GPU laptop, ADR 0015):

    uv run python -m banking_analysis.extraction.runner
"""

from __future__ import annotations

import logging

from banking_analysis.extraction.client import OllamaClient
from banking_analysis.extraction.extractor import extract_campaign
from banking_analysis.extraction.store import pending_runs, save_result
from banking_analysis.storage.db import connect

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("extraction_run")


def main() -> None:
    model = OllamaClient()
    log.info("model server: %s (%s)", model.url, model.model)

    with connect() as conn:
        runs = pending_runs(conn)
        log.info("%d collection run(s) pending extraction", len(runs))

        ok = dropped = no_campaign = failed = 0
        for run_id, bank_id, url, raw_text in runs:
            result = extract_campaign(raw_text, model)
            if not result.ok:
                failed += 1
                log.warning("run %d FAILED: %s", run_id, result.failure_reason)
                continue
            save_result(conn, run_id, bank_id, url, result)
            if result.is_no_campaign:
                no_campaign += 1
            else:
                ok += 1
            if result.diagnostics:
                dropped += 1
                for d in result.diagnostics:
                    log.info("run %d — %s", run_id, d)

        log.info(
            "done: %d extracted, %d no-campaign, %d failed, %d had dropped fields",
            ok, no_campaign, failed, dropped,
        )


if __name__ == "__main__":
    main()
