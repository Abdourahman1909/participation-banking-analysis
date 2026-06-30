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
  all verified working. File Map added to `CLAUDE.md`.
- Docker installed on user's laptop (Ubuntu 22.04, 7.6 GB RAM). Postgres
  container running and verified: schema created, all 10 banks seeded,
  `docker compose up postgres -d` confirmed healthy. Postgres uses ~25 MB.
- **Layer 1 → Layer 4 pipeline verified end-to-end for the first time:**
  ran `scheduler/run_collection.py` against live Postgres — 13 campaigns
  stored in `collection_runs` (Kuveyt Türk 10/10 OK, T.O.M. 3/3 OK).
  Raw Turkish campaign text confirmed readable in the database.
- Placeholder Streamlit dashboard running at `http://localhost:8501`
  (start with: `uv run streamlit run src/banking_analysis/frontend/dashboard.py`)

## Blocked on this machine (needs the team's actual hardware)

- **No GPU/Ollama here** — extraction (ADR 0004/0005, Qwen2.5-Instruct)
  hasn't been started. Needs the teammate's laptop with the actual GPU.
  7.6 GB RAM means CPU-only Ollama will be very tight; confirm GPU/VRAM
  on teammate's machine before choosing 7B vs 14B.

## Next (immediate — do in order)

1. **Build remaining 8 bank scrapers** — each requires manually visiting
   the bank's campaign page first to find the URL + CSS selector + page
   shape (Shape 1: list→detail pages like Kuveyt Türk, or Shape 2: all
   campaigns on one page like T.O.M.). ~15 min per bank. Banks remaining:
   Albaraka Türk, Türkiye Finans, Vakıf Katılım, Ziraat Katılım,
   Türkiye Emlak Katılım, Dünya Katılım, Adil Katılım, Hayat Finans.
2. Build the extraction engine (ADR 0004) — on the GPU machine
3. Build rule-based validation (ADR 0008)
4. Build the tool-calling agent + real dashboard/chatbot (ADR 0007/0009/0012)
5. Decide the project name
6. Push all of the above to the private repo as it lands
