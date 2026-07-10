-- Knowledge Store schema (ADR 0006). Plain relational tables, no ORM.
-- pgvector is NOT enabled here — reserved for later per ADR 0006, add via
-- `CREATE EXTENSION vector;` + an embedding column if/when it's ever needed.

CREATE TYPE campaign_type AS ENUM (
    -- the 8 types named in the competition spec (§5.4), plus a catch-all.
    -- Closed enum, not free text — see ADR 0011.
    'funding',
    'personal_financing',
    'housing_finance',
    'vehicle_financing',
    'card',
    'shopping_points',
    'new_customer',
    'investment_product',
    'other'
);

CREATE TABLE banks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    website TEXT NOT NULL,
    is_digital BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per scraper execution (ADR 0003: scheduled batch only, never
-- live). ok=false rows are kept for audit, but the campaigns table only
-- ever reflects the most recent ok=true run per (bank, url) — that's how
-- Stale Bank Data (CONTEXT.md) works: a failed run doesn't overwrite the
-- last known-good text.
CREATE TABLE collection_runs (
    id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(id),
    url TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    ok BOOLEAN NOT NULL,
    failure_reason TEXT,
    raw_text TEXT  -- only set when ok = true
);

CREATE INDEX idx_collection_runs_bank_url_fetched
    ON collection_runs (bank_id, url, fetched_at DESC);

-- One row per campaign found in a piece of source text. is_no_campaign
-- captures ADR 0014's explicit "this text wasn't a campaign" outcome as a
-- real row (so we know the source was processed), rather than silently
-- skipping it, which would be indistinguishable from "not processed yet".
CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(id),
    collection_run_id INTEGER NOT NULL REFERENCES collection_runs(id),
    source_url TEXT NOT NULL,
    campaign_type campaign_type,
    title TEXT,
    is_no_campaign BOOLEAN NOT NULL DEFAULT FALSE,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_campaigns_bank_type ON campaigns (bank_id, campaign_type);

-- One row per Extracted Field (CONTEXT.md): {value, evidence_quote} pair,
-- both nullable together when the source text doesn't state that field
-- (ADR 0014 — null is a valid outcome, not a failure). is_valid/
-- validation_reason are ADR 0008's deterministic rule-based check,
-- null until that check has run.
CREATE TABLE campaign_fields (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,        -- e.g. 'profit_share_rate', 'maturity_months', 'cost_amount'
    value TEXT,                      -- verbatim/as-extracted string; never overwritten (ADR 0017)
    value_normalized NUMERIC,        -- typed, comparable value produced by validation (ADR 0008/0017)
    evidence_quote TEXT,             -- verbatim source sentence; null iff value is null
    is_valid BOOLEAN,                -- rule-based validation verdict (Layer 3); null = not checked / no value
    validation_reason TEXT,
    UNIQUE (campaign_id, field_name)
);

CREATE INDEX idx_campaign_fields_name_value ON campaign_fields (field_name, value);

-- Pipeline run activity (ADR 0021/0022): each operator/API-triggered layer
-- run and its structured events (the monitor UI's timeline). Append-only
-- (ADR 0017) — only a run's finish status is filled in when it ends. The
-- API also creates these idempotently at startup (banking_analysis/api/
-- runs.py DDL) so databases created before ADR 0022 get them; keep the two
-- definitions in sync.
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id          SERIAL PRIMARY KEY,
    step        TEXT NOT NULL,           -- collection | extraction | validation
    started_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    ok          BOOLEAN                  -- null while running
);

CREATE TABLE IF NOT EXISTS pipeline_events (
    id          SERIAL PRIMARY KEY,
    run_id      INTEGER NOT NULL REFERENCES pipeline_runs(id),
    seq         INTEGER NOT NULL,
    event_type  TEXT NOT NULL,           -- bank_done, page_fetched, … or raw 'log'
    payload     JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_events_run ON pipeline_events (run_id, seq);
