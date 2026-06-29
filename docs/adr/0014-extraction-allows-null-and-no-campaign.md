---
status: accepted
---

# Extraction schema allows null fields and an explicit "no campaign detected" outcome

Building on ADR 0010's point that bank pages won't reliably look the way we
expect: the campaign/promotion *text* itself is just as unpredictable as the
page structure — it might mix multiple campaigns in one block, use an
unfamiliar format, omit fields the schema expects, or not describe a
campaign at all. The extraction prompt (ADR 0004) must not assume every
scraped block cleanly matches the schema. Concretely: every field is
nullable (the LLM returns null rather than guessing or force-fitting a
plausible-looking value when something isn't actually stated), and the
schema includes an explicit `no_campaign_detected` outcome the LLM can
return instead of a populated record. Validation (ADR 0008) treats null as
a valid, non-failing state — a missing field is not the same as a failed
field.
