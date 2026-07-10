# Layer 4 — Storage ("one database, and nothing is ever deleted")

## What it does

Holds everything the system knows, in one place: the **Knowledge Store**.
Every other layer either writes into it or reads from it — layers never
talk to each other directly, they meet at the database.

## What we use

**PostgreSQL** — the world's most trusted open-source database — running
in Docker. One database, a handful of tables:

| Table | Holds |
|---|---|
| `banks` | The 10 BDDK participation banks |
| `collection_runs` | Every raw text snapshot ever collected (Layer 1's output) |
| `campaigns` + `campaign_fields` | Extracted values + evidence quotes + validation verdicts (Layers 2–3) |
| `pipeline_runs` + `pipeline_events` | What the system did and when (the Monitör's timeline) |

## The two big ideas

**1. Append-only — never delete, never overwrite.**
A new collection doesn't replace the old one; it adds a new snapshot.
Validation doesn't overwrite the extracted text; it writes its clean
number in a *separate column*. Why: history is evidence. If a bank changes
a rate, we can show both versions and when they changed. If a bug corrupts
something, yesterday's truth still exists. Deleting data destroys the one
thing you can't recreate.

**2. The "Current View" — history underneath, freshness on top.**
If we keep every snapshot, won't counts double? No: whenever the system
needs "the situation now," it computes the *latest good snapshot per bank
and page* on the fly. History stays underneath; the surface always shows
current reality.

## Where the data physically lives

Inside a **Docker volume** on the machine — not in the project folder, not
on GitHub. Cloning the repository copies **code only**; each machine grows
its own data by running collection. Data survives restarts and rebuilds;
only one deliberate command (`docker compose down -v`) can erase it.

## If someone asks…

- *"Why Postgres and not something fancier (vector DB, NoSQL)?"* — "Our
  data is naturally tabular — banks, campaigns, fields. Postgres is
  reliable, free, and if the project grows, pgvector adds AI-search inside
  the same database. No migration later."
- *"What if two extractions disagree?"* — "Both are kept with timestamps;
  the Current View shows the newest, history keeps the older one."
