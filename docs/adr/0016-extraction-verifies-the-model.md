---
status: accepted
---

# Extraction treats the model as an untrusted proposer and verifies it

We run a small, cheap local model (Qwen2.5 7B/14B, ADR 0005/0015), not a
frontier model. We must not design extraction on the expectation that its
output is correct. The design stance: **the model proposes; deterministic
code verifies before anything is trusted or stored.** A wrong answer must
never reach the user looking like a fact.

Concretely, extraction (Layer 2):

1. **Constrained, deterministic decoding.** Output is forced to JSON and
   parsed with a strict schema; `temperature = 0`. `campaign_type` is coerced
   to the closed enum (ADR 0011), unknown values folded to `other`.
2. **Null is a first-class, encouraged answer (ADR 0014).** The prompt tells
   the model to return null when the text doesn't state a field, and never to
   guess or compute. A model forced to always produce a number fabricates;
   removing that pressure is itself a defense.
3. **Grounding gate (the core check).** For every field the model must return
   the verbatim `evidence_quote` it took the value from. Our code verifies
   that quote is actually a substring of the source text (whitespace/case
   normalized). **If the quote isn't in the source, the value and quote are
   dropped to null and the failure is logged** — a value the model can't
   ground in the bank's own words is never stored as a value. (Decision:
   drop, don't keep-and-mark — the strongest "never show an unverified
   number" posture.)
4. **Failures are distinct from absence.** Malformed output or an ungrounded
   quote is recorded as a failure, kept separate from a legitimate "this
   field isn't stated" or "no campaign here" (ADR 0014).

Division of labour with validation (ADR 0008, Layer 3): extraction guarantees
**groundedness** (the quote is real, copied from the source); validation
judges **correctness** (does the value match its quote? plausible
range/format?) and sets `is_valid`. Both implement "verify, don't trust" at
their own level. This sharpens ADR 0004 — the evidence quote is now a
verification gate, not just a citation.

Measurement over expectation: because the grounding/parse logic is
deterministic, extraction is **fully testable offline** by feeding fake model
outputs (including hallucinated quotes) through the verifier — no GPU needed
to prove the safety logic. Separately, a hand-built **ground-truth answer
key** over the already-collected real texts lets us *measure* extraction
accuracy on real data once the model is online, rather than assuming 7B is
good enough; if it underperforms, escalate to 14B or tighten the prompt.
