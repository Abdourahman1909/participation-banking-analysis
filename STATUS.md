# Status

## Done

- Competition spec and architecture research read and understood (`A01/`)
- Full system architecture resolved via a grilling session — 14 ADRs in
  `docs/adr/`, glossary in `CONTEXT.md`
- Scrapling explored against actual project needs; ADR 0002/0010 amended
  with real findings (fetcher tiering, the `relocate()` self-check
  mechanism)
- `CLAUDE.md` and this file set up for cross-session continuity
- Private GitHub repo created and pushed: github.com/Abdourahman1909/participation-banking-analysis
- Confirmed the real BDDK bank list: 10 active banks, not the ~7 assumed
  (ADR 0001) — 7 traditional, 3 digital-only
- Project scaffolded (`uv`, `src/banking_analysis/` package layout)
- Two real per-bank scrapers built and tested against live sites:
  - Kuveyt Türk (list page → 10 detail pages, one CSS selector each) — 10/10 OK
  - T.O.M./Hadi (3 campaigns inline on one page, non-adjacent siblings,
    needed a `run()` override) — 3/3 OK
  - Found and fixed an over-strict self-check (content-marker requirement)
    that false-flagged legitimate campaigns lacking a numeric rate
- Postgres schema written (`db/schema.sql`, `db/seed_banks.sql`) —
  banks / collection_runs / campaigns / campaign_fields, matching every
  CONTEXT.md term
- Storage layer (`src/banking_analysis/storage/db.py`) wiring scrapers to
  the schema
- `docker-compose.yml` + `scheduler/Dockerfile` + `app/Dockerfile` per
  ADR 0013, plus a placeholder Streamlit app that reads the Knowledge Store

## Blocked on this machine (needs the team's actual hardware)

- **No Docker installed** (no passwordless sudo to install it) — the
  compose stack, schema, and storage layer are written but not yet run
  end-to-end against a real Postgres instance. Needs validating on a
  machine with Docker.
- **No GPU/Ollama here** — extraction (ADR 0004/0005, Qwen2.5-Instruct)
  hasn't been started. Needs the teammate's laptop with the actual GPU.

## Next

- Confirm GPU/VRAM on the team's laptop -> lock Qwen2.5 7B vs 14B, install
  Ollama there, validate the docker-compose stack end-to-end
- Build remaining 8 bank scrapers (pattern is proven for both page shapes
  seen so far; some banks may need a 3rd shape, or `DynamicFetcher` if
  JS-rendered — not yet encountered)
- Build the extraction engine (ADR 0004): LLM call -> {value, evidence_quote}
  per field, closed enum for campaign_type (ADR 0011), nullable fields +
  no_campaign_detected (ADR 0014)
- Build rule-based validation (ADR 0008)
- Build the tool-calling agent + real dashboard/chatbot (ADR 0007/0009/0012)
- Decide the project name
- Push all of the above to the private repo as it lands
