---
status: accepted
---

# The pipeline monitor lives in the product UI, with run triggers

## Context

The frontend rebuild (ADR 0020, brief in `docs/frontend-rebuild-brief.md`)
has three surfaces: comparison dashboard, chatbot, and a polished
pipeline-activity view. Today, running the pipeline means clicking a button
in the Streamlit control panel (ADR 0018) or a terminal command, then
watching raw Scrapling logs (`Fetched (200)…`, `Kuveyt Türk: 10/10
collected`). The open question: does the polished monitor live inside the
new product UI, and does it replace the control panel or coexist with it?

Two forces: (1) the user's pain is *both* triggering and watching — a
watch-only monitor would still bounce them back to the control panel to
start a run; (2) PRODUCT.md's primary audience is TEKNOFEST judges who need
to "see the collect→extract→compare→answer pipeline working" in minutes.

## Decision

The monitor is a **first-class third view inside the new unified UI**, and
it **includes the run triggers** (start collection / extraction /
validation) alongside a live activity timeline, per-bank progress, the
collected→extracted→validated funnel, and model-server reachability.

Run buttons in the public product are acceptable because the system is
on-prem: everyone with network access to the UI is an operator by
definition. There is no untrusted-public deployment in scope (competition
demo and on-prem startup deployments alike).

The **Streamlit control panel stays**, reduced to internal deep tools: the
read-only SQL console, table browser, and eval runs. It is no longer the
primary way to run the pipeline once the new monitor reaches parity.

## Consequences

- Strongest possible demo: one screen where a judge watches a click on
  "Topla" light up banks live — the pipeline visibly working inside the
  polished product.
- The API layer must expose pipeline operations, not just data reads:
  status, run-triggering, and a live activity feed (contract in the API
  ADR). The agent itself stays read-only (ADR 0007) — only the pipeline
  endpoints mutate, and they only append (ADR 0017).
- The activity view renders structured events (bank, count, status), not
  raw log text — the terminal-log experience is explicitly what this
  replaces.
- If a genuinely public deployment ever happens (startup path), the
  pipeline endpoints need auth before that ships. Not a competition
  concern; noted so it isn't forgotten.
