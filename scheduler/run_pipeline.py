"""Scheduled full batch pipeline (ADR 0003, 0013): collect → extract →
validate, then sleep and repeat.

Interval via PIPELINE_INTERVAL_SECONDS (default 86400 = daily). Best-effort:
a failing step is logged and does NOT stop the others or crash the loop — so
if the model server is offline, collection + validation still run and
extraction simply logs failures until the model is back.

This is what the `scheduler` container runs (docker-compose.yml). Each step is
the same runnable module the control panel and CLI use.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("pipeline")

STEPS = [
    ("collection", ["uv", "run", "python", "-m", "banking_analysis.collection.runner"]),
    ("extraction", ["uv", "run", "python", "-m", "banking_analysis.extraction.runner"]),
    ("validation", ["uv", "run", "python", "-m", "banking_analysis.validation.runner"]),
]
INTERVAL = int(os.environ.get("PIPELINE_INTERVAL_SECONDS", "86400"))
WORKDIR = os.environ.get("PIPELINE_WORKDIR", "/app")


def run_once() -> None:
    for name, cmd in STEPS:
        log.info("=== %s ===", name)
        result = subprocess.run(cmd, cwd=WORKDIR)
        log.info("%s finished (exit %d)", name, result.returncode)


def main() -> None:
    while True:
        run_once()
        log.info("pipeline cycle done; sleeping %d s", INTERVAL)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
