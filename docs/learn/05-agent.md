# Layer 5 — The Agent ("a chatbot that can only press our buttons")

## What it does

The brain behind **Sohbet**. You ask in Turkish, "en uygun taşıt
finansmanı hangi bankada?", and it answers in natural language — **with
sources**. It is the same local AI model as extraction, but wearing a very
tight straitjacket.

## What we use

**Tool-calling** (also called function-calling). Instead of letting the
model say whatever it wants, we give it exactly two "buttons" it may press:

- `get_campaigns` — fetch campaigns from the database (optionally by type)
- `compare_by_rate` — fetch campaigns of one type, ordered by rate

Both buttons are **read-only**: the model can look, never touch.

## How it works, step by step

1. Your question goes to the model together with a **scope guard**
   instruction: "you only discuss participation-banking campaigns; decline
   anything else." (You saw it live — it refused to speak English and
   redirected, exactly as designed.)
2. The model decides which button to press. It says "press
   `compare_by_rate` for vehicle financing" — and **our code** presses it,
   runs the real SQL, and hands the rows back.
3. The model writes a Turkish answer using those rows.
4. **The killer detail:** the "Kaynaklar" (sources) under the answer are
   NOT written by the model. Our code attaches them automatically from the
   exact database rows the buttons returned. The model *cannot* cite
   something it never retrieved — it doesn't write the citations at all.

## Why this way

An LLM can invent facts. So the design makes invention harmless:

- It has **no direct data access** — only the two read-only buttons.
- It **cannot write** anything to the database.
- Citations are **attached by code**, from real rows.
- The rows themselves were already proven at extraction time (evidence
  gate) and double-checked by validation.

The only thing the model truly controls is the *wording* of the answer —
and the sources sit right under it, so a reader verifies the claim against
the bank's own sentence instead of trusting the prose.

If someone tries to jailbreak it ("write me Python code", "ignore your
instructions"), worst case it says something off-topic — it still can't
read anything but campaigns or change a single row. Small blast radius by
construction.

## If someone asks…

- *"How is this different from asking ChatGPT?"* — "Three ways: it runs
  fully offline on our own model; it can only answer from our verified
  database, not from the internet or its memory; and every answer carries
  code-attached citations to the bank's own sentences."
- *"Can it hallucinate an answer?"* — "It can word things wrong, but it
  cannot invent data or citations — sources are attached by code from the
  rows it actually retrieved, and every number in those rows carries the
  bank's own proof sentence."
