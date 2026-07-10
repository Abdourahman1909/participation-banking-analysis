# Hard questions people will ask — and your answers

Short answers you can say out loud. Practice the bold ones; they're the
most likely (judges, teammates, technical exam).

## About the AI

**"LLMs hallucinate. How do you deal with that?"**
"We assume the model lies. It's an untrusted proposer: every value it
extracts must carry a verbatim quote from the bank's text, and our code
verifies the quote really exists — otherwise the value is dropped. Then a
second, rule-based layer checks the value matches its own quote. And in
the chatbot, citations are attached by code from real database rows, so
it can't invent a source."

**"Why not just use ChatGPT / GPT-4?"**
"The competition requires fully on-prem, offline operation — no external
AI APIs, no data leaving the organization. We run Qwen 2.5, an open-source
model, on our own hardware via Ollama. It's also free and private."

**"How do you know your extraction is accurate?"**
"We built a ground-truth answer key — real pages with hand-checked correct
values — and an evaluation harness that measures the model against it.
We measure accuracy; we don't assume it."

**"Your laptop has no GPU. How do you run a model?"**
"The model runs on a teammate's GPU machine; our code reaches it over the
local network. Same on-prem network, still offline to the outside world."

## About the data

**"What if a bank's website changes and breaks your scraper?"**
"Already happened — two pages 404'd two days after we built that scraper.
Every scrape runs a self-check; failures are flagged, the last known-good
snapshot is kept and honestly labeled as stale. The monitor shows every
failure. Nothing breaks silently."

**"Do you delete outdated campaigns?"**
"Never. Append-only: new snapshots are added, history stays. The interface
computes a 'current view' — newest good snapshot per page — so users see
fresh data while the full history remains underneath as evidence."

**"Is any user or customer data involved?"**
"No. We only collect public marketing pages from bank websites. The
chatbot stores no conversations today; if we ever do, it's designed to be
KVKK-aware from the start."

## About the engineering

**"How do you test a system that needs a model and live websites?"**
"Everything is testable offline: 40+ automated tests run with fake models
and fake data — they prove the evidence gate catches hallucinated quotes,
validation catches misread values, the agent never invents sources, and
the API degrades gracefully when the database is down. No GPU needed to
verify the logic."

**"Can this scale / become a product?"**
"The pieces were chosen to grow: Postgres scales and adds vector search
without migration, the API boundary means mobile apps reuse the backend
as-is, scrapers are one small file per new bank. The architecture doesn't
need replacing after the competition."

**"Why is the whole thing in Docker?"**
"One command starts the database, the model server, the scheduled
pipeline, and both interfaces on any machine — teammates and judges get an
identical system without installing Python or Postgres by hand."

## The one-line identity

If you remember nothing else:

> **"KıyasAI makes participation-banking campaigns comparable — and every
> number in it can prove itself with the bank's own sentence."**
