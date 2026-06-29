# CLAUDE.md

Orientation for Claude Code (or any contributor) at the start of a session
in this repo.

## Project

TEKNOFEST 2026 AI Language Agents Competition, Scenario 2: Participation
Banking Product Analysis System. Collects campaign data from Turkish
participation banks, extracts structured financial fields via a local LLM,
makes products comparable across banks, and serves results via a dashboard
+ chatbot.

## Where things live

- `A01/` — original competition spec and architecture research (read in
  numbered order, 1 through 5)
- `CONTEXT.md` — domain glossary (project vocabulary, sharpened terms)
- `docs/adr/` — architecture decisions, numbered, each with the why
- `STATUS.md` — current progress and immediate next steps

## Standing constraints (from the competition spec, non-negotiable)

- Must run fully on-prem/offline — no external LLM APIs, no paid services,
  no customer data leaving the organization
- Open-source only — no dependency with licensing risk
- Code, datasets, and docs must be shared on GitHub, tagged
  `BilisimVadisi2026`, updated at least weekly; final license is Apache 2.0

## Before assuming the architecture

Read `docs/adr/` before recommending or changing any part of the design —
it's the source of truth, not a summary of a past conversation.
