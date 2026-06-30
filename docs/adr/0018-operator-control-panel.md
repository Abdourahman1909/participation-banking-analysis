---
status: accepted
---

# A separate operator control panel, with read-only SQL

Until now the pipeline is operated from the terminal — running the scrapers,
extraction, and validation by hand. That's fine for development but not a way
for the team to run and watch the system. We're adding an **operator control
panel**: a Streamlit app (Streamlit is mediocre for a polished public product
but excellent for internal admin tools) that wraps the existing runners with
buttons, shows pipeline status, and lets the operator inspect the data.

It is a **separate app** from the public dashboard (ADR 0012), on its own
port — different audience (operator vs end user), so the public dashboard
stays clean and ops controls aren't exposed to end users.

What it does:
- **Run** each layer on demand (collection, extraction, validation, eval) via
  the same runners, output shown in the panel.
- **Status** — table counts, the collected→extracted→validated funnel, model
  server reachability, scraper coverage, last run times.
- **Data browser** — pre-built views of each table.
- **SQL console** — type a query, see results (what the terminal gave before).

Two guards:

1. **The SQL console is read-only.** Only `SELECT`/`WITH` queries run; write/DDL
   keywords are refused *and* the query runs over a connection set
   `read_only`, so the database itself rejects any write. This protects the
   append-only asset (ADR 0017): inspection must never be able to delete or
   overwrite history. Data is *changed* only through the pipeline runners,
   never by hand-edited SQL.
2. **Manual run ≠ agent live-scrape.** A "Run Collection" button is an
   operator manually triggering the batch job — consistent with ADR 0003,
   which forbids the *agent* triggering a live scrape mid-conversation, not a
   human running the batch on demand.

The control panel is a cross-cutting operations tool, not a pipeline layer —
it lives in `src/banking_analysis/control_panel/` and depends on every layer
rather than being one.
