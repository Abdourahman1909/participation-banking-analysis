---
status: accepted
---

# Deterministic rule-based validation, not an LLM-judge confidence scorer

File 4 names Validation/QC as its own layer (consistency checks, hallucination
reduction, confidence scores). With evidence quotes already captured (ADR
0004), we're validating with deterministic rules only: a sanity check that
each field's normalized `value` is substantiated by its `evidence_quote`,
plus per-field-type format/range validators (percentages in a sane range,
maturity as a positive integer, parseable dates). Each field gets a pass/
fail flag, not a fuzzy confidence score. A second LLM-judge pass was
considered and rejected: it adds real cost and latency for a dataset this
small, without a clear accuracy advantage over rules, and pass/fail rules
are easier to explain to a judge than an opaque confidence number.
