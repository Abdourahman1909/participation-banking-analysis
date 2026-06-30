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
2. ~~Build the extraction engine (ADR 0004)~~ — **code done** (Layer 2,
   ADR 0016 verify-don't-trust). `src/banking_analysis/extraction/`:
   client (Ollama over `OLLAMA_URL`), prompt, models, extractor (grounding
   gate — drops any value whose evidence quote isn't in the source), store,
   runner, eval. 7/7 offline tests pass (`tests/test_extraction.py`) proving
   the verifier catches hallucinated quotes — no GPU needed. STILL TO DO:
   run it against the real model on the GPU laptop, then `eval` to measure
   accuracy (7B vs 14B decision) on the ground-truth answer key.
3. ~~Build rule-based validation (ADR 0008)~~ — **code done** (Layer 3).
   `src/banking_analysis/validation/`: normalize (Turkish number parsing),
   validator (substantiation = value's number is in its quote; parse; range),
   store, runner. Added `value_normalized` column to campaign_fields (typed
   value; original string kept, ADR 0017). Dashboard now sorts on the stored
   normalized value (dropped the ad-hoc `_parse_rate`). 14/14 offline tests
   pass (`tests/test_validation.py`). Runs with no model/GPU:
   `uv run python -m banking_analysis.validation.runner` (after extraction).
4. ~~Build the tool-calling agent (ADR 0007)~~ — **code done** (Layer 5).
   `src/banking_analysis/agent/`: fixed read-only toolset (get_campaigns,
   compare_by_rate), scope-guard prompt (banking domain only; clarify +
   recommend in-scope, decline off-topic), tool-calling loop with sources
   attached deterministically from tool results (ADR 0009). Wired into the
   dashboard chat with graceful fallback to the canned preview until
   campaigns exist + the model is reachable. 3/3 offline tests pass. STILL
   TO DO: run against the real model on the GPU laptop.
   **All 6 layers are now code-complete (24/24 offline tests pass).** The
   remaining work is operational: run extraction + validation + agent against
   the real model on the GPU laptop (ADR 0015), then the full pipeline is
   live end-to-end.
5. Decide the project name (UI currently uses the working title "Katılım
   Compare" — not final)
6. Data-lifecycle follow-ups (ADR 0017, build when Collection Runs start
   repeating): a Current View query (latest snapshot per bank+URL), persist
   extraction drops/diagnostics for model-quality tracking, Postgres backup
   cadence. Principle locked: append-only, never delete — history is the asset.
7. Push all of the above to the private repo as it lands

## Parked ideas (good, but deliberately deferred)

- **Conversation-data asset.** The user↔chatbot interaction traces (question →
  tools → sources → answer → verdict) are a valuable second asset: real query
  demand signal, training/eval data for a better model, quality measurement.
  BUT conversations can contain personal data → must be privacy-by-design and
  KVKK-aware (Turkey's data-protection law); on-prem already helps. Parked on
  2026-07-01 (no real users yet). When revived: append-only conversation_log
  per ADR 0017 (session id, not identity), privacy policy first. Not built.
