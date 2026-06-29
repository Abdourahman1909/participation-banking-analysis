---
status: accepted
---

# Use Scrapling as the Layer-1 collection library

Considered building per-bank scrapers from scratch (requests/BeautifulSoup,
or Playwright directly) versus adopting an existing OSS scraping framework.
We're using Scrapling (BSD-3-Clause, adaptive element selection, handles
both static requests and full browser automation under one API) as the
collection library: its adaptive selectors tolerate bank site redesigns
without rewrites, its license satisfies the competition's open-source
requirement (spec §5.10), and it scales from "7 known pages" today to
broader crawling later if the project continues past the competition as a
startup — avoiding a framework migration. Confirmed final after the rest of
the architecture (extraction, storage, reasoning, validation, frontend) was
designed consistently on top of it with no objection.

**Amendment (post source-read):** Scrapling exposes three fetcher tiers —
`Fetcher` (plain HTTP, no browser), `DynamicFetcher` (Playwright, JS
rendering), `StealthyFetcher` (Playwright + anti-bot fingerprint evasion).
Each bank scraper defaults to the cheapest tier (`Fetcher`) and only
escalates to `DynamicFetcher`/`StealthyFetcher` for the specific banks that
turn out to need JS rendering or hit anti-bot protection — not uniformly
across all 7. This keeps the deployment image small for banks that never
need Chromium (see ADR 0013's Docker footprint).
