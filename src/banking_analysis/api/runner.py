"""Serve the API + SPA (ADR 0022). Same entry-point convention as the layers:

    uv run python -m banking_analysis.api.runner        # http://localhost:8000
"""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "banking_analysis.api.app:app",
        host=os.environ.get("API_HOST", "0.0.0.0"),
        port=int(os.environ.get("API_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
