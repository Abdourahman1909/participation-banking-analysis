# Frontend rebuild brief — professional unified UI (handoff for a dedicated session)

**Status:** planned, not started. Written 2026-07-10 to hand a fresh session
full context. The current Streamlit dashboard stays working until the
replacement is ready — do not delete it mid-build.

## Objective

Replace the Streamlit public frontend with **one professional, unified web
interface** that puts the **comparison dashboard and the chatbot in a single,
polished product** — not two separate Streamlit tabs. This is the competition's
public face (TEKNOFEST evaluators are the primary audience, see `PRODUCT.md`).
The Streamlit **control panel** (operator console, ADR 0018) is internal and
can stay Streamlit — only the *public* frontend is being rebuilt.

This swap is explicitly allowed by **ADR 0012** (Streamlit was chosen *behind a
clean backend boundary* precisely so it could be replaced later without touching
the backend).

**Three surfaces, one professional product** (user confirmed 2026-07-10):
1. **Comparison dashboard** — the public product face.
2. **Chatbot** — in the same unified UI, not a separate tab.
3. **Operational / pipeline-activity view** — a *polished* way to watch the
   system work. Today the user runs the pipeline and stares at raw Scrapling
   terminal logs (`Fetched (200) …`, `Kuveyt Türk: 10/10 campaigns collected`,
   `T.O.M.: 3/3`, extraction running). They want this — and everything like it
   (collection progress, per-bank results, extraction/validation status, live
   run activity) — shown **cleanly and professionally**, not as terminal output.
   This is a first-class requirement, not an afterthought. Open question for the
   new session: does this live inside the new UI as an "operations/monitor"
   view, and how does it relate to the Streamlit control panel (ADR 0018) —
   replace it, or keep control panel internal and add a polished read-only
   monitor to the product? Decide via grilling; record an ADR.

**Brand is locked and user-approved.** The KıyasAI teal-green + diamond-mark
identity in the just-submitted team-introduction PDF is the confirmed look —
inherit it exactly (see `DESIGN.md`), do not redesign the brand.

## The architectural prerequisite — design this FIRST

The Streamlit app calls Python functions in-process. A real web frontend can't
do that, so the **first deliverable is an HTTP API layer (recommend FastAPI)**
in front of Layers 4 (storage) and 5 (agent). This is:
- **Additive** — no change to the six existing layers; it wraps them.
- **The same API the future mobile app needs** (see the mobile-app plan in
  memory) — build it once, both clients use it.
- Best done on a **branch** in this repo.

Design the API contract before writing UI. Minimum endpoints (mirror what the
current `dashboard.py` already does):
- `GET /api/campaigns?type=<optional>` → the comparison rows. Shape already
  used today: `bank, title, campaign_type, profit_share_rate, maturity_months,
  cost_amount, evidence_quote, value_normalized, is_valid`.
- `GET /api/stats` → header counts (banks, campaigns, last collection time).
- `POST /api/chat` `{question}` → the agent's **answer + sources** contract
  (ADR 0009): `{answer, sources:[{bank, title, field, value, evidence_quote}]}`.
- (later) `GET /api/banks`, history/export for the analyst audience.
- **Operational view** (surface 3): `GET /api/pipeline/status` → the funnel +
  per-bank coverage + last-run times + model reachability (reuse
  `control_panel/ops.py: status()/model_status()`). `POST /api/pipeline/run`
  → trigger collect/extract/validate. For **live activity** (the polished
  replacement for the Scrapling terminal logs), stream progress/log lines via
  Server-Sent Events or WebSocket, or poll a `GET /api/pipeline/runs` feed —
  decide in the new session. Render as a clean activity timeline, not raw logs.

Reuse the existing code: `banking_analysis.storage.db` and
`banking_analysis.agent.agent.answer(...)`. Keep the agent **read-only**.

## Non-negotiable constraints (these score competition points)

- **Fully offline / on-prem.** No CDN, no external fonts, no external API calls
  from the browser. Bundle every asset locally (self-host fonts, inline/ship
  JS+CSS). The built frontend is served locally (e.g. FastAPI static mount or a
  local Node/Nginx container in `docker-compose.yml`).
- **Open-source / permissive licenses only** (MIT/Apache/BSD). No
  licensing-risk dependency.
- **Turkish-first UI.** Same as today (see `PRODUCT.md`).
- **Evidence transparency is the product's soul.** Every extracted value must
  show its **verbatim evidence quote** (ADR 0016) and the chatbot must show
  **sources** (ADR 0009). A prettier UI must not drop this — it's what proves
  the numbers are real to the judges.
- The dev-only external model API (ADR 0019) is backend-side; the frontend
  never talks to a model directly, only to our own `/api`.

## Reuse — brand & design already exist, honor them

- **Brand: KıyasAI** (teal-green, calm-analytical light theme; deliberately not
  finance-navy). Wordmark + teal diamond mark.
- **`DESIGN.md`** — keep the **brand foundations**: OKLCH palette (`--brand` =
  `#0F8A77`), the teal-green identity, logo, typographic intent. Port these
  tokens into the new stack (CSS variables / Tailwind theme). BUT its
  component/layout specs were written for Streamlit's constraints — treat those
  as history, not a mandate. The new UI's layout and components are a fresh
  professional design; refresh `DESIGN.md` to match once the new direction lands.
- **`PRODUCT.md`** — audiences, register, principles ("clarity and evident
  correctness beat feature breadth").
- The current `dashboard.py` is a **reference for BEHAVIOR ONLY** — the data
  shown, filter/sort, best-rate highlight, Panel + Sohbet, graceful fallback to
  sample data. **It is NOT the visual target.** The user explicitly does *not*
  like the current dashboard and chat *design* (a Streamlit limitation —
  stacked widgets, weak layout control, no real custom components). Redesign
  the layout and components fresh and professionally; do not port the Streamlit
  look. Only the **brand** (color + logo) is being kept, not the current UI.

## Recommended stack (confirm via grilling in the new session)

- **Frontend:** React + Vite + TypeScript (SPA, builds to static assets that
  serve fully offline). Next.js only if SSR is truly wanted — likely overkill.
- **Styling/components:** Tailwind CSS + shadcn/ui (Radix primitives) — all
  MIT, professional, you own the components. Charts: Recharts or visx (MIT).
- **API:** FastAPI (Python, reuses the layers). Serves JSON + the built SPA.
- **Fonts:** self-hosted (no Google Fonts CDN) to stay offline.
- All MIT/permissive → competition-safe.

## First-session plan (grill one decision at a time, record ADRs)

1. Confirm the stack above (or adjust). → **ADR** (this is hard-to-reverse).
2. Design the `/api` contract. → **ADR** for the boundary + endpoints.
3. Build FastAPI wrapping storage + agent; test against the live DB.
4. Scaffold the frontend; port `DESIGN.md` tokens; build the unified shell
   (dashboard + chat in one view).
5. Wire to the API; keep the evidence-quote + sources transparency.
6. Dockerize the new frontend into `docker-compose.yml`; keep it offline.
7. Keep Streamlit dashboard until parity is reached, then switch `app/` over.

## Do NOT change

- The six backend layers, the data contracts (`value_normalized`, evidence
  quotes, the answer+sources shape), the append-only data lifecycle (ADR 0017).
- The KıyasAI brand and the design principles.
- The offline/on-prem and licensing constraints.

## Read these first (new session)

`PRODUCT.md`, `DESIGN.md`, `CONTEXT.md`, `docs/adr/0012` (boundary), `0009`
(answer+sources), `0007` (agent), `0016` (evidence), `0017` (data lifecycle),
`0018` (control panel stays Streamlit), plus `db/schema.sql`, and the current
`src/banking_analysis/frontend/dashboard.py` as the behavior reference.
