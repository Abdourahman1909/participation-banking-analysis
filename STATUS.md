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

- Layer reorganization done: `app/streamlit_app.py` moved to
  `src/banking_analysis/frontend/dashboard.py`, `app/Dockerfile` updated,
  each layer's `__init__.py` has a comment identifying which layer it is —
  all verified working. File Map added to `CLAUDE.md`. These changes are
  uncommitted (staged).
- Docker installed on the user's laptop (Ubuntu 22.04). Postgres container
  verified end-to-end: schema created, all 10 banks seeded, `docker compose
  up postgres -d` confirmed healthy. RAM on this machine: 7.6 GB total;
  Postgres uses ~25 MB.

## Blocked on this machine (needs the team's actual hardware)

- **No GPU/Ollama here** — extraction (ADR 0004/0005, Qwen2.5-Instruct)
  hasn't been started. Needs the teammate's laptop with the actual GPU.
  7.6 GB RAM means CPU-only Ollama will be very tight; confirm GPU/VRAM
  on teammate's machine before choosing 7B vs 14B.

## Next (immediate — do in order)

1. **Commit** the staged layer-reorganization changes (last session ended
   before committing)
2. **Wire scrapers → `collection_runs`**: the scraper writes `raw_text`
   to the `collection_runs` table (Layer 1 → Layer 4 handoff). Storage
   layer connector exists in `src/banking_analysis/storage/db.py` but
   hasn't been called from the scrapers yet. This is the correct next
   step — it does NOT skip Layers 2/3; those read from `collection_runs`
   later when the GPU machine is available.
3. **Build remaining 8 bank scrapers** (pattern proven for both page
   shapes seen so far; some may need `DynamicFetcher` if JS-rendered —
   not yet encountered)
4. Build the extraction engine (ADR 0004) — on the GPU machine
5. Build rule-based validation (ADR 0008)
6. Build the tool-calling agent + real dashboard/chatbot (ADR 0007/0009/0012)
7. Decide the project name
8. Push all of the above to the private repo as it lands
