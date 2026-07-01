---
status: accepted
---

# No separate Cleaning layer, but per-bank scrapers self-check and flag failure

Building on ADR 0001 (hand-mapped per-bank extractors): rather than a
generic HTML→Markdown/noise-stripping layer, each scraper targets the
bank's known content region directly via Scrapling selectors, so output is
already close to clean. But bank websites change without notice and don't
owe us a stable structure — assuming the selector "just keeps working" is
unfounded. Each scraper run checks its own output for anomalies (empty
result, drastically shorter/longer than the last successful run, missing
expected markers like a `%` sign or currency symbol) and marks that bank's
Collection Run as failed rather than passing suspect content downstream. A
failed run keeps serving the last known-good data (with a visible "stale
since" indicator) instead of silently overwriting good data with garbage
from a broken selector.

**Amendment (post source-read):** Scrapling's adaptive-selector engine
(`Selector.relocate()`) already produces part of this signal for free: when
no element scores above its similarity threshold against a previously saved
reference, it returns empty and logs a warning rather than silently
returning nothing useful — that empty result is a ready-made anomaly
trigger, not something we need to detect ourselves from scratch. Caveat:
`relocate()` only tracks the *first* matched element per saved identifier,
so a bank page listing multiple campaigns needs one identifier per
repeating field (not one for the whole list) — more bookkeeping than a
single-element selector. For banks where the campaign block is a single
known element, this is a clean win; for banks listing several campaigns per
page, weigh it against just asserting non-emptiness directly in our own
code, which needs no per-identifier setup.

**Correction (post first real scraper, Kuveyt Türk):** initially tried
adding a content-marker check (require a `%` or `TL` in the extracted
text) as part of self-check. Live testing immediately produced false
positives — legitimate campaigns (an interest-free-installment promo on a
partner site, a favorable-FX offer) don't always state a flat numeric rate.
That's exactly the nullable-field case ADR 0014 already covers, not a
scraping anomaly. Self-check stays purely structural: empty result, or
length far outside the expected range for that selector. Whether a field
has a value is extraction's problem, not collection's.

**Correction 2 (post second real Collection Run, 2026-07-01):** a legitimate
Kuveyt Türk campaign (a long cost table) came back at 20,003 chars and was
false-flagged by a 20,000-char `max_length` cap — a 0.015% overage rejecting
good data. Same lesson as above: the self-check must catch only *drastically*
wrong output (e.g. the selector grabbed the whole page), not a hair over an
arbitrary line. Raised the default ceiling to 50,000 (per-bank overrides
likewise). The same run also produced 2 genuine `HTTP 404`s — campaigns
removed from the bank's site between runs — which the check correctly failed,
preserving the last known-good data (Stale Bank Data). The design worked; only
the one threshold was too tight.
