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
