# Layer 2 — Extraction ("the AI that reads, and the gate that checks it")

## What it does

Turns free Turkish campaign text into **structured fields**: profit share
rate (kâr payı), term in months (vade), amount (tutar), campaign type.
This is the only place where an AI model does real work — and it is also
where we trust it the least.

## What we use

- **Qwen 2.5**, an open-source AI model, running on **Ollama** — a program
  that serves AI models on your own computer. Nothing goes to the cloud.
  (The competition explicitly forbids external AI APIs; this is scored.)
- Our machine has no GPU, so the model runs on a teammate's GPU laptop and
  our code talks to it **over the local network** — same idea as any web
  API, but inside the room. During development we can temporarily use an
  external API (Groq) hosting the same model family — clearly marked
  dev-only, never in the submission.

## How it works, step by step

1. Extraction asks the database: "which collected pages have I not
   processed yet?" (Only new work — running it twice is safe.)
2. For each page, the model receives the raw text and must answer in a
   strict format: each field's **value** PLUS an **evidence quote** — the
   exact sentence from the text that states the value.
3. **The gate (our key idea):** our code checks that the quote *really
   exists*, word for word, inside the source text. The model is a smart
   intern; the gate is the boss who checks receipts.
   - Quote is real → the value is saved, with its quote.
   - Quote not found (the model paraphrased or invented) → **the value is
     thrown away** and the drop is logged. We store nothing unproven.
4. A field the text simply doesn't mention is stored as **null** — an
   honest "unknown", never a guess. A page that isn't a campaign at all is
   marked "no campaign".

## Why this way

AI models **hallucinate** — they confidently invent plausible numbers.
You cannot stop that with a polite prompt. So the design treats the model
as an **untrusted proposer**: it proposes, deterministic code verifies.
You have seen it work live: `dropped value '%2,96': evidence quote not
found in source` — that was the gate rejecting a paraphrased proof.

There is also an **accuracy exam**: a hand-made answer key of real pages
and their correct values, so we can *measure* how good the model actually
is instead of assuming.

## If someone asks…

- *"How do you prevent AI hallucination?"* — "We don't prevent it, we
  catch it. Every value must carry a verbatim quote from the source; code
  verifies the quote is really there, or the value is dropped."
- *"Why a local model instead of ChatGPT?"* — "Competition rule: fully
  offline, no external AI, no data leaving the organization. Also cost and
  privacy."
- *"What if the model misses a value?"* — "It's stored as null and shown
  as '—'. We never fabricate completeness."
