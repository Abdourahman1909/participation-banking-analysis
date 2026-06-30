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
- **Layer 6 frontend designed and built** (ADR 0012, via the `impeccable`
  skill). Strategic brief in `PRODUCT.md`, visual system in `DESIGN.md`.
  Calm-analytical light theme, teal-green brand. Three files under
  `src/banking_analysis/frontend/`: `theme.py` (OKLCH CSS design system),
  `sample_data.py` (illustrative extracted campaigns from real scraped
  text), `dashboard.py` (header + live stats, comparison Panel with
  filter/sort/best-rate highlight, Sohbet chat showing the ADR 0009
  answer+sources contract). `.streamlit/config.toml` holds the base theme.
  Verified end-to-end with headless-browser screenshots. Start with:
  `uv run streamlit run src/banking_analysis/frontend/dashboard.py`
  - Real data: bank list + collection stats from Postgres. Extracted
    fields are sample data (badged "Önizleme") until Layer 2 runs; the
    dashboard auto-switches to the DB once campaigns are populated.

## Model server: teammate's GPU laptop (ADR 0015)

- This machine has **no usable GPU** (Intel iGPU, 7.6 GB RAM) — confirmed
  with `nvidia-smi`. Cannot run the extraction/agent model here.
- **Decision (ADR 0015):** run Ollama + Qwen2.5 on a teammate's GPU laptop
  as a network model server; the rest of the system runs on the primary
  machine and reaches it via `OLLAMA_URL` over the LAN. Still on-prem.
- **One number still needed:** the GPU's VRAM (`nvidia-smi` on that laptop)
  to lock 7B vs 14B (ADR 0005). On that machine:
  `curl -fsSL https://ollama.com/install.sh | sh` then
  `ollama pull qwen2.5:7b-instruct` (or `:14b-instruct`).
- Extraction code can be **written now** on this machine (it just points
  `OLLAMA_URL` at the GPU laptop) — not blocked on having the hardware yet.

## Next (immediate — do in order)

1. **Build remaining 8 bank scrapers** — each requires manually visiting
   the bank's campaign page first to find the URL + CSS selector + page
   shape (Shape 1: list→detail pages like Kuveyt Türk, or Shape 2: all
   campaigns on one page like T.O.M.). ~15 min per bank. Banks remaining:
   Albaraka Türk, Türkiye Finans, Vakıf Katılım, Ziraat Katılım,
   Türkiye Emlak Katılım, Dünya Katılım, Adil Katılım, Hayat Finans.
2. Build the extraction engine (ADR 0004) — on the GPU machine
3. Build rule-based validation (ADR 0008)
4. Build the tool-calling agent (ADR 0007) and wire it to the existing
   chat UI — the frontend shell + answer/sources layout already exist
   (Sohbet tab); they need the real LLM agent behind them instead of the
   canned responses. Same for the comparison Panel: it reads real DB data
   automatically once extraction populates campaigns/campaign_fields.
5. Decide the project name (UI currently uses the working title "Katılım
   Compare" — not final)
6. Push all of the above to the private repo as it lands
