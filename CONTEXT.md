# Participation Banking Product Analysis System

Domain glossary for the TEKNOFEST 2026 Scenario 2 project: an NLP system that
collects, extracts, and compares financial product information from
participation banks operating in Turkey.

## Language

**Participation Bank**:
A bank regulated under Turkey's interest-free finance principles, using
profit-share rates instead of interest and financing instead of credit. The
official, regulator-recognized category for what's colloquially called an
"Islamic bank."
_Avoid_: Islamic bank (informal), conventional bank (different category)

**Target Bank List**:
The fixed, finite set of participation banks officially listed by the BDDK
(Banking Regulation and Supervision Agency) that the system collects campaign
data from — confirmed as 10 active banks as of 2026-06-29 (7 traditional, 3
digital-only; see ADR 0001). The boundary of what the system scrapes is
closed and enumerable, not an open-ended crawl target.
_Avoid_: the web, crawl targets, bank universe

**Collection Run**:
A scheduled, batch execution of the Layer-1 scrapers across the Target Bank
List that refreshes stored campaign data. The only way new data enters the
system — the chatbot/agent never fetches a page itself mid-conversation.
_Avoid_: live scrape, on-demand fetch, real-time lookup

**Extracted Field**:
A single structured data point produced by the Structured Extraction Engine,
represented as a `{value, evidence_quote}` pair rather than a bare value —
`value` is the normalized form, `evidence_quote` is the verbatim source
sentence it was derived from. Both may be null when the source text doesn't
state that field; null is a valid outcome, not a failure.
_Avoid_: raw value, scraped field (these imply no evidence is attached)

**Knowledge Store**:
The single Postgres database holding all Extracted Fields for the Target
Bank List. The system's only persistent store — retrieval is plain SQL
filtering, not embedding similarity search. Carries unused `pgvector`
capacity for future semantic search if data volume grows.
_Avoid_: vector DB, semantic store (these imply embedding-based retrieval,
which isn't in use)

**Validated Field**:
An Extracted Field that has passed deterministic rule-based checks (its
`value` is substantiated by its `evidence_quote`; it's plausible for its
field type — range, format, date parseability). Carries a pass/fail flag,
not a fuzzy confidence score.
_Avoid_: confidence score, verified field (these imply a continuous score
rather than a binary deterministic check)

**Stale Bank Data**:
Data for a bank whose most recent Collection Run failed its self-check
(empty or anomalous extraction) and was discarded; the system keeps serving
the last known-good data with a visible "stale since" indicator rather than
overwriting it with suspect content.
_Avoid_: failed bank, broken bank (these describe the bank, not the data
state)

**Campaign Type**:
One of the 8 categories named in the competition spec (Funding, Personal
Financing, Housing Finance, Vehicle Financing, Card, Shopping Points, New
Customer, Investment Product) plus an `Other` catch-all — a closed
classification assigned to every extracted campaign, not free text, so
cross-bank comparison can group on it.
_Avoid_: campaign category (implies open-ended)

**Snapshot**:
The data captured by one Collection Run for one source URL at one point in
time — the raw text and everything extracted from it, tied to that run's
`fetched_at`. The store is append-only (ADR 0017): re-scraping the same URL
later creates a *new* snapshot, it never overwrites the old one, so snapshots
accumulate into a per-bank time series.
_Avoid_: the latest data, the record (these hide that history is kept)

**Current View**:
The query-time selection of the most recent Snapshot per (bank, source URL)
— what the dashboard shows as "available now." It is a *view* over the
history, not a stored table; producing it never deletes older Snapshots
(ADR 0017).
_Avoid_: current table, live data (imply older data was replaced/removed)

**Campaign Lifecycle State**:
The status of a campaign as a value that changes over time — e.g. active
(its validity window contains today) vs expired (window has passed) — derived
from extracted date fields. Expiry is a *state*, never a deletion: an expired
campaign stays in the store as the historical record of a promotion that ran
(ADR 0017).
_Avoid_: deleting/removing expired campaigns, archived (implies moved out)

**Provenance**:
The traceable lineage of any stored figure back to its origin —
`campaign_field → campaign → collection_run → raw_text`, plus its
`evidence_quote` (ADR 0004) and validation verdict (ADR 0008). Guarantees any
value can be tied to the exact source text, bank, and timestamp it came from.
_Avoid_: source link (understates the full chain + timestamp)
