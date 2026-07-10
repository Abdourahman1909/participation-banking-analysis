"""Serve the API + SPA (ADR 0022). Same entry-point convention as the layers:

    uv run python -m banking_analysis.api.runner        # http://localhost:8000
"""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def load_env_file(path: Path) -> None:
    """Minimal `.env` loader so local `uv run` matches docker compose (which
    reads `.env` natively). KEY=VALUE lines only; real environment variables
    always win; pipeline subprocesses inherit whatever is loaded here."""
    try:
        text = path.read_text()
    except OSError:
        return
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def main() -> None:
    load_env_file(PROJECT_ROOT / ".env")
    uvicorn.run(
        "banking_analysis.api.app:app",
        host=os.environ.get("API_HOST", "0.0.0.0"),
        port=int(os.environ.get("API_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
