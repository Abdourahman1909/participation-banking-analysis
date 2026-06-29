# Status

## Done

- Competition spec and architecture research read and understood (`A01/`)
- Full system architecture resolved via a grilling session — 14 ADRs in
  `docs/adr/`, glossary in `CONTEXT.md`
- Scrapling library explored against actual project needs; ADR 0002 and
  ADR 0010 amended with concrete findings (fetcher tiering, the adaptive
  `relocate()` self-check mechanism and its list-extraction caveat)
- `CLAUDE.md` and this file set up for cross-session continuity

## Next

- Confirm the exact BDDK-listed participation bank list
  (https://www.bddk.org.tr/Kurulus/Liste/77)
- Decide the project name
- Confirm GPU/VRAM available on the team's laptop -> lock Qwen2.5 7B vs 14B
- Start implementation: per-bank Scrapling scrapers (ADR 0002/0010)
- Set up the GitHub remote (tag `BilisimVadisi2026`, weekly updates)
