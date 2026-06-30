"""Layer 3 — Validation. See docs/adr/0008, 0017.

Deterministic rule-based checks on extracted fields: substantiation (value's
number is in its evidence quote), parse/normalize (typed value_normalized,
original string kept), and range/format plausibility. Sets is_valid +
validation_reason. Code complete; 14/14 offline tests pass. Run after
extraction: uv run python -m banking_analysis.validation.runner
"""
