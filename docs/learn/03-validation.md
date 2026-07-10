# Layer 3 — Validation ("the boring double-check, and boring is the point")

## What it does

Takes every value that survived extraction and checks it again — with
**plain rules, no AI at all**. It answers a different question than the
extraction gate did:

- Extraction's gate asked: *"is the proof sentence real?"* (groundedness)
- Validation asks: *"does the value actually match its proof, and does it
  make sense?"* (correctness)

## What we use

Pure Python. No model, no GPU, no network. It runs anywhere in a second.

## How it works, step by step

1. It picks up every field that has a value but no verdict yet.
2. **Substantiation check:** the value's number must appear inside its own
   evidence quote. This catches a subtle failure: the model quoted a real
   sentence but *misread it* — e.g. the quote says %2,96 but the model
   wrote 2,69 as the value.
3. **Turkish number normalization:** Turkish writes numbers as `%2,96` and
   `300.000 TL` (comma = decimal, dot = thousands). Validation converts
   these into clean machine numbers — 2.96 and 300000 — so sorting and
   comparing works correctly.
4. **Sanity ranges:** a monthly profit rate of 45% or a term of 600 months
   is flagged as invalid — real campaigns don't look like that.
5. The verdict (valid / invalid + reason) is written next to the value. The
   original text is **never** modified; the clean number is stored in a
   separate column.

## Why this way

Checking "is 2,96 inside this sentence?" needs certainty, not
intelligence. Using an AI to check an AI would just add a second liar to
the room. Rules are deterministic: same input, same verdict, every time —
and they're testable offline (this layer has 14 automated tests).

The interface then sorts campaigns by the *clean validated number*, never
by re-reading the display text — one source of truth for comparisons.

## If someone asks…

- *"Why do you validate if extraction already verifies?"* — "Different
  jobs. Extraction proves the quote is real; validation proves the value
  matches the quote and is plausible. The second check has already caught
  models misreading their own quotes."
- *"Why no AI here?"* — "This is arithmetic and string checking. Rules are
  100% reliable and free; a model is neither."
