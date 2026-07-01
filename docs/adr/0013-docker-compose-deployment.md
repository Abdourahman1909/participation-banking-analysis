---
status: accepted
---

# Single docker-compose stack for on-prem deployment

On-Prem Feasibility is 20% of the competition score (§7), and the
deliverables require step-by-step run instructions (§6). We're packaging
the architecture as one `docker-compose.yml` with four services mapping
directly onto existing decisions: `postgres` (Knowledge Store, ADR 0006),
`ollama` (serving Qwen2.5 locally, ADR 0005), `app` (Streamlit dashboard +
chatbot, ADR 0012), and `scheduler` (runs the Scrapling Collection Run on a
cron schedule, ADR 0002/0003). One `docker compose up` brings up the whole
system — no new components, just packaging what's already designed. This
turns the on-prem claim into something demonstrable rather than asserted,
and is the realistic deploy story if the project continues as a startup.

**Amendment (post-build, 2026-07-01):** the stack now matches all the built
layers. The `scheduler` service runs the **full batch pipeline** —
collect → extract → validate (`scheduler/run_pipeline.py`) on an interval
(`PIPELINE_INTERVAL_SECONDS`, default daily) — not just collection; each step
is a runnable module (`-m banking_analysis.<layer>.runner`) so it's the same
code the control panel and CLI use. A **control-panel** service (ADR 0018) was
added on its own port (8502), reusing the app image with a different command.
Two operational notes: the `ollama` service starts empty, so the model must be
pulled once (`docker compose exec ollama ollama pull qwen2.5:7b-instruct`), or
skipped entirely by pointing `OLLAMA_URL` at a GPU host (ADR 0015); and the
scheduler is deliberately *not* hard-depended on `ollama`, so that external-
model setup works and a missing model degrades (extraction logs failures)
rather than blocking collection/validation.
