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

**Amendment (post-build, with ADR 0016/0017):** the division of labour with
extraction is now explicit. Extraction (ADR 0016) guarantees *groundedness* —
the evidence quote is verbatim from the source, or the value is dropped.
Validation owns *correctness*: (1) **substantiation** — the value's number
actually appears in its evidence quote (catches the model misreading its own
quote, e.g. value 3,96 against a quote that says 2,96); (2) **range/format**
plausibility per field type. **Normalization lives here too:** validation
parses the as-extracted string into a typed value and emits it alongside the
pass/fail flag — it has to parse to range-check anyway, so the typed value is
a byproduct, and the frontend no longer parses strings ad hoc. Per ADR 0017
the typed value is written to a **new** `value_normalized` column; the
original `value` string is never overwritten (provenance preserved).
Null-valued fields (legitimately not stated, ADR 0014) are not validated —
`is_valid` stays null. Implemented in `src/banking_analysis/validation/`.
