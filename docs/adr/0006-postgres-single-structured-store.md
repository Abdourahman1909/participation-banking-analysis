---
status: accepted
---

# Postgres as the single Knowledge Store; no separate vector DB

File 5's hybrid memory layer (vector DB + Postgres) solves a search problem
we don't have yet: the Target Bank List is ~7 banks with a handful of
campaigns each, small enough that the model's context window holds the
whole relevant slice directly — embedding-based similarity search adds an
embedding model, an indexing step, and a new failure mode for no benefit at
this scale. We're using a single Postgres database for all extracted
records (values + evidence quotes), with retrieval done as plain SQL
filtering rather than vector search. Postgres over SQLite specifically
because of `pgvector`: if the dataset grows later (more institutions, more
content, the startup path), semantic search can be added via an extension
and an embedding column on the same database, instead of migrating off
SQLite or bolting on a separate vector DB system. The same
"don't pick a tool you'll replace later" reasoning as ADR 0002 (Scrapling).
