# CLAUDE.md

Orientation for Claude Code (or any contributor) at the start of a session
in this repo.

## Project

TEKNOFEST 2026 AI Language Agents Competition, Scenario 2: Participation
Banking Product Analysis System. Collects campaign data from Turkish
participation banks, extracts structured financial fields via a local LLM,
makes products comparable across banks, and serves results via a dashboard
+ chatbot.

## Where things live

- `A01/` — original competition spec and architecture research (read in
  numbered order, 1 through 5)
- `CONTEXT.md` — domain glossary (project vocabulary, sharpened terms)
- `docs/adr/` — architecture decisions, numbered, each with the why
- `STATUS.md` — current progress and immediate next steps

## File Map — which folder is which architecture layer

Every layer's actual code lives under `src/banking_analysis/<layer>/` —
open any file there and its `__init__.py` says which layer it is and which
ADRs explain it. Top-level `app/`, `scheduler/`, `db/` are deployment glue
only (Dockerfiles, SQL) — they don't contain layer logic themselves.

| Layer | Code lives in | Deployment glue |
|---|---|---|
| 0 — Data sources | (just the bank list, ADR 0001) | `db/seed_banks.sql` |
| 1 — Collection | `src/banking_analysis/collection/` | `scheduler/Dockerfile` runs `scheduler/run_collection.py` |
| 2 — Extraction | `src/banking_analysis/extraction/` | `extraction/runner.py` (`-m banking_analysis.extraction.runner`) |
| 3 — Validation | `src/banking_analysis/validation/` | `validation/runner.py` (`-m banking_analysis.validation.runner`) |
| 4 — Knowledge Store | `src/banking_analysis/storage/` (the connector) | `db/schema.sql` (the actual schema) |
| 5 — Reasoning (agent) | `src/banking_analysis/agent/` | — (wired into the frontend chat) |
| 6 — Frontend | `src/banking_analysis/frontend/` | `app/Dockerfile` runs `frontend/dashboard.py` |
| (wraps all of it) | — | `docker-compose.yml` |

All six layers are code-complete as of 2026-07-01 (offline-tested in
`tests/`). If a folder under `src/banking_analysis/` is empty, that layer
hasn't been built — check `STATUS.md` for current state.

**Not a layer:** `src/banking_analysis/control_panel/` is a cross-cutting
operator console (ADR 0018) — buttons to run each layer, status, data
browser, read-only SQL. Run it on its own port:
`uv run streamlit run src/banking_analysis/control_panel/app.py --server.port 8502`

## Technical constraints (these score points, keep them regardless of path)

- Must run fully on-prem/offline — no external LLM APIs, no paid services,
  no customer data leaving the organization
- Open-source/permissively-licensed dependencies only — no library with
  licensing risk

## Competition disclosure rules — the user's call, not a default

The spec (file 2, §8-9) requires public GitHub sharing, weekly updates, the
`BilisimVadisi2026` tag, and final Apache 2.0 licensing as a condition of
competition participation. The user has explicitly flagged that this
project may continue as their own startup after the competition, and that
*they* decide how to weigh competition compliance against protecting that
path — not something to assume or push toward by default. Don't treat the
public-sharing/licensing terms as settled; ask before doing anything that
makes the repo public, changes its license, or publishes it more broadly.

**Routine pushes to the private repo are different from disclosure** —
nobody sees them but the user. Commit and push to `origin` (private) at
natural checkpoints during a session without asking each time. The
ask-first rule applies only to visibility/license changes, not to backup
hygiene on an already-private remote.

## Before assuming the architecture

Read `docs/adr/` before recommending or changing any part of the design —
it's the source of truth, not a summary of a past conversation.
