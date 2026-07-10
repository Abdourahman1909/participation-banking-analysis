# The Big Picture — explain KıyasAI in 2 minutes

> This folder teaches you the system in plain words — no code. One file per
> layer. Read this file first; read the others in any order. The deep
> technical "why" for every decision lives in `docs/adr/`.

## The one-paragraph story

Turkish participation banks (katılım bankaları) publish campaigns on their
websites as free text — every bank writes differently, so people cannot
compare them. **KıyasAI reads all 10 banks' campaign pages automatically,
uses an AI model to pull out the numbers that matter (profit rate, term,
amount), proves every number with the bank's own sentence, and shows
everything in one place** — a comparison table and a chatbot, both in
Turkish. The special thing is not the AI; it's that **we never trust the
AI**: a number only enters our database if the bank's own text proves it.

## The factory (six layers)

Think of it as a factory line. Each layer has ONE job and passes its work
to the next:

```
 Bank websites
      │
 [1] COLLECTION   — robots visit the 10 banks, save the raw text
      │
 [2] EXTRACTION   — an AI model reads the text, proposes the numbers
      │               (every number must carry a proof sentence)
 [3] VALIDATION   — plain rules double-check the numbers (no AI here)
      │
 [4] STORAGE      — everything lives in one database, nothing is deleted
      │
 [5] AGENT        — the chatbot brain: answers questions using ONLY the
      │               database, and cites its sources
 [6] FRONTEND     — what people see: the KıyasAI web app
```

## What we use (the tools, and one reason each)

| Part | Tool | Why in one sentence |
|---|---|---|
| Collection | **Scrapling** (Python) | Web scraper that can tell us when a bank changed its page instead of silently breaking |
| Extraction | **Qwen 2.5** on **Ollama** | A local open AI model — the competition forbids external AI services like ChatGPT |
| Validation | Plain Python rules | Checking numbers needs certainty, not intelligence |
| Storage | **PostgreSQL** | One boring, reliable database everyone trusts; grows with us after the competition |
| Agent | Tool-calling on the same local model | The model may only "press buttons" we built; it can't touch data directly |
| Frontend | **React** web app + **FastAPI** (Python) | A professional interface; the API layer lets a future mobile app reuse everything |
| Packaging | **Docker** | The whole system starts on any machine with one command |

## The three sentences to remember

1. **"Fully offline and on-prem"** — no data leaves the machine, no external
   AI APIs, no paid services. This is a scored competition requirement.
2. **"Every number carries its proof"** — each extracted value is stored
   with the verbatim sentence from the bank's page that proves it. If the
   AI can't quote a real sentence, the value is thrown away.
3. **"Append-only"** — we never delete or overwrite data. New collections
   add snapshots; history stays. If something looks wrong today, we can
   always look at what the site said yesterday.

## If someone asks: "so what did YOU build, exactly?"

"A system that makes Islamic-banking campaigns comparable. Ten banks,
scraped on a schedule; a local LLM extracts structured fields but is
treated as an untrusted proposer — deterministic code verifies every value
against the source text and drops anything unproven; results go into
Postgres and are served through a FastAPI + React interface with a
comparison dashboard, a source-citing chatbot, and a live pipeline
monitor. Everything runs offline in Docker."
