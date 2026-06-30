---
status: accepted
---

# Append-only data lifecycle: the historical record is a first-class asset

The system accumulates several kinds of data — raw scraped text, failed
scrapes, extracted fields, fields flagged invalid, and (later) expired vs
active campaigns. How we manage their lifecycle is an architecture decision,
not an implementation detail, because the project may continue as a startup
(see the project's startup framing) where the **accumulated history is the
moat**: rate/term time series per bank, campaign seasonality, and a labelled
dataset of model successes/failures for training a better model later.

Decision: **the data store is append-only and provenance-preserving. Nothing
is ever deleted or overwritten — data changes *state*, not existence.**

Concretely:

- **Raw text** (`collection_runs`) is the immutable archive: every Collection
  Run is kept, timestamped, success or failure (`ok=false` rows retained with
  `failure_reason`). Re-scraping the same URL appends a new row; it never
  overwrites the previous one. This is the time series.
- **Provenance is mandatory.** Every extracted value traces back through
  `campaign_fields → campaigns.collection_run_id → collection_runs.raw_text`
  plus its `evidence_quote` (ADR 0004) and validation verdict (ADR 0008). Any
  figure can be tied to the exact source text, bank, and timestamp it came
  from, at any past date.
- **Invalidity and expiry are states, not deletions.** A field that fails
  validation is flagged (`is_valid=false`, `validation_reason`), not removed.
  An expired campaign is marked expired (once date fields exist), not deleted
  — it becomes the historical record of a promotion that ran.
- **"Current" is a query, not a mutation.** The dashboard's "what's available
  now" is a *view* over the latest snapshot per (bank, source_url); it does
  not delete older snapshots to produce it.

Consequences / what this commits us to (built when collection actually
repeats, designed now so the schema evolves coherently):

- A **Current View** query (latest snapshot per bank+URL) once Collection
  Runs repeat and snapshots accumulate.
- Campaign validity dates as extracted fields to drive the active/expired
  **Campaign Lifecycle State** (deferred per the user's call, but the lifecycle
  is expiry-as-state when added).
- Optionally persisting extraction-time drops/diagnostics (ADR 0016) so model
  quality can be measured over time, not just logged.
- A backup/retention cadence (Postgres dumps) to protect the growing asset.

Explicit non-goal: there is **no "cleanup old rows" job.** Anyone tempted to
prune history for tidiness is destroying the asset this ADR exists to protect.
Postgres + reserved `pgvector` capacity (ADR 0006) scales to this volume.
