---
status: accepted
---

# Scope data acquisition to the fixed BDDK-listed participation bank set

The competition spec requires covering "all institutions... as listed on
BDDK's official website," which is a small, named, finite list (~6-8 banks).
We're scoping the system's data acquisition layer to this Target Bank List
rather than building a generic, open-ended web crawler. Generic crawling,
anti-bot evasion, and proxy rotation solve a problem we don't have; a handful
of hand-mapped, per-bank extractors is simpler to build, debug, and keep
on-premise-compliant, and matches the actual deliverable. If the project
later expands beyond the competition (e.g. into a startup covering more
institutions), this boundary can be revisited — but it should not be
designed around speculatively now.

**Confirmed list (fetched from bddk.org.tr/Kurulus/Liste/77, 2026-06-29):**
10 active participation banks, not the ~6-8 originally assumed — 3 of them
digital-only banks, which likely present campaigns differently (app-centric,
thinner marketing sites) than the 7 traditional ones:

| Bank | Website | Type |
|---|---|---|
| Albaraka Türk Katılım Bankası | albarakaturk.com.tr | Traditional |
| Kuveyt Türk Katılım Bankası | kuveytturk.com.tr | Traditional |
| Türkiye Finans Katılım Bankası | turkiyefinans.com.tr | Traditional |
| Vakıf Katılım Bankası | vakifkatilim.com.tr | Traditional |
| Ziraat Katılım Bankası | ziraatkatilim.com.tr | Traditional |
| Türkiye Emlak Katılım Bankası | emlakbank.com.tr | Traditional |
| Dünya Katılım Bankası (ex-Adabank) | dunyakatilim.com.tr | Traditional |
| Adil Katılım Bankası | adilkatilim.com.tr | Digital |
| Hayat Finans Katılım Bankası | hayatfinans.com.tr | Digital |
| T.O.M. Katılım Bankası | tombank.com.tr | Digital |

Note: bddk.org.tr's own TLS certificate fails standard validation (had to
fetch with cert verification disabled) — a one-off for this lookup, not
relevant to the bank scrapers themselves, which hit each bank's own site.

**First two scrapers built and confirmed against live sites (2026-06-29):**
Kuveyt Türk (list page → 10 individual campaign detail pages, one
`.campaign-detail` selector) and T.O.M./Hadi (3 campaigns inline on one
listing page, title+description and terms as non-adjacent siblings —
needed a `run()` override instead of the list-of-URLs pattern). Both work
with the plain HTTP `Fetcher`, no JS rendering needed.

T.O.M. Bank's consumer brand is "Hadi" — its marketing domain
(hadiyanindakibanka.com) turned out to be a JS-rendered search/FAQ shell our
plain fetch can't read, so we scrape the corporate domain
(tombank.com.tr/kampanyalar.html) instead, which serves real campaign
content directly. Worth re-checking if that page ever stops listing real
campaigns — the Hadi domain may need `DynamicFetcher` if it becomes the
only source later.
