---
status: accepted
---

# An HTTP API layer (FastAPI) in front of storage, agent, and pipeline

## Context

The Streamlit dashboard calls Python functions in-process. The new SPA
frontend (ADR 0020) — and the planned mobile app — cannot; they need HTTP.
ADR 0012 kept the intelligence layers behind a clean internal boundary
precisely so a real frontend could be added without touching them. This ADR
turns that boundary into an explicit, versionable HTTP contract.

The monitor decision (ADR 0021) adds a requirement beyond data reads: the
API must trigger pipeline steps and stream live run activity to the browser.

## Decision

A **FastAPI** app in `src/banking_analysis/api/` — a boundary adapter, not a
new layer. It wraps existing code only: `storage.db`, `agent.agent.answer`,
the control panel's `ops` queries, and the layer runners. It also serves the
built SPA as static files, so one process is the whole public product.

### Contract (v1 — field names English like the schema, UI strings Turkish)

Read (mirror what `frontend/dashboard.py` shows today):
- `GET /api/stats` → `{banks, campaigns, last_collection}` — Current View
  counts (ADR 0017: distinct ok bank+url, not total runs).
- `GET /api/campaigns?type=<enum>` → `{items: [...], is_sample}`. Item:
  `{bank, title, campaign_type, profit_share_rate, maturity_months,
  cost_amount, evidence_quote, rate_normalized, term_months, is_valid}`.
  `rate_normalized`/`term_months` come from `value_normalized` (ADR 0008/
  0017) — clients sort on those, never re-parse display strings.
  `is_sample=true` marks the illustrative fallback (DB empty/down); the UI
  must badge it as preview, same honesty rule as today.
- `POST /api/chat` `{question}` → `{answer, sources: [{bank, title, field,
  value, evidence_quote}], is_preview}` — the ADR 0009 answer+sources shape,
  verbatim. `is_preview=true` when the canned fallback answered (no data or
  no model). Non-streaming for now: the agent's tool loop returns a complete
  answer; a spinner is honest. Token streaming can be added later without
  breaking this shape.

Pipeline (ADR 0021):
- `GET /api/pipeline/status` → funnel counts + scraper coverage + model
  reachability (wraps `control_panel.ops.status()` / `model_status()`).
- `POST /api/pipeline/run` `{step}` (collection | extraction | validation)
  → `202 {run_id}`. Runs the step as a background subprocess (same commands
  as `ops.STEPS`); one run at a time per step.
- `GET /api/pipeline/runs` → recent runs (step, started/finished, outcome).
- `GET /api/pipeline/runs/{id}/events` → **Server-Sent Events** stream of
  structured events (`step_started`, `bank_started`, `page_fetched`,
  `bank_done {collected, total}`, `warning`, `step_done`). Chosen over
  WebSocket (two-way channel buys nothing for a one-way feed) and polling
  (delayed, chattier); SSE is plain HTTP, auto-reconnects, works offline.

### Events are stored, the stream is a view

New append-only tables `pipeline_runs` and `pipeline_events` (ADR 0017
compliant — insert-only, never updated except run finish status). The API
parses the runners' stdout lines into structured events as they arrive:
parsing lives in the API adapter, so **no changes to the six layers**. If a
line doesn't parse, it's stored as a raw `log` event — nothing is dropped.
History survives refreshes; the SSE stream replays stored events then tails.

## Consequences

- The SPA, the future mobile app, and any script consume one contract; the
  Streamlit dashboard keeps its in-process path until retired.
- Pipeline endpoints mutate (append-only) — fine on-prem (ADR 0021); needs
  auth before any genuinely public deployment.
- The agent stays read-only (ADR 0007); `/api/chat` adds no write path.
- Two schema tables are added via an idempotent migration in `db/`; existing
  tables untouched.
- Evidence transparency is structural: `evidence_quote` is in the campaigns
  item and the chat source shape — a client can't render values without
  having the proof available.
