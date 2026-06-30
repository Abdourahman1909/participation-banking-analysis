"""Layer 2 — Extraction. See docs/adr/0004, 0011, 0014, 0016.

Code complete and unit-tested offline (verify-don't-trust, ADR 0016).
Not yet run against the real model — needs the GPU model server (ADR 0015).
Run with: uv run python -m banking_analysis.extraction.runner
Measure quality with: uv run python -m banking_analysis.extraction.eval
"""
