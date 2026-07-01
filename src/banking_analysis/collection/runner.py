"""Layer 1 — batch Collection Run (ADR 0003: scheduled batch only, never
agent-triggered). Runs every registered bank scraper and saves results to the
Knowledge Store. Importable/runnable like the other layers:

    uv run python -m banking_analysis.collection.runner
"""

from __future__ import annotations

import logging

from banking_analysis.collection.banks.kuveytturk import KuveytTurkScraper
from banking_analysis.collection.banks.tombank import TomBankScraper
from banking_analysis.storage.db import connect, get_or_create_bank, save_collection_result

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("collection_run")

# Add a scraper here as each bank gets built (ADR 0001: 10 banks total).
SCRAPERS = [KuveytTurkScraper, TomBankScraper]


def main() -> None:
    with connect() as conn:
        for scraper_cls in SCRAPERS:
            scraper = scraper_cls()
            bank_id = get_or_create_bank(
                conn, scraper.name, scraper.base_url,
                is_digital=getattr(scraper, "is_digital", False),
            )
            results = scraper.run()
            ok_count = sum(1 for r in results if r.ok)
            log.info("%s: %d/%d campaigns collected", scraper.name, ok_count, len(results))
            for result in results:
                save_collection_result(conn, bank_id, result)
                if not result.ok:
                    log.warning("%s FAILED: %s — %s", scraper.name, result.url, result.failure_reason)


if __name__ == "__main__":
    main()
