# Layer 1 — Collection ("the robots that visit the banks")

## What it does

Visits the campaign pages of the 10 BDDK participation banks and saves the
**raw text** of every campaign into our database. Raw means: exactly what
the bank wrote, untouched. No interpretation happens here.

## What we use

- **Scrapling** — a Python web-scraping library. We chose it over simpler
  tools for one killer feature: it can *notice change*. If a bank redesigns
  its page, Scrapling can often relocate the content, and when it can't, it
  tells us — instead of silently returning garbage.
- One small **scraper per bank**, because every bank's website is shaped
  differently. Two shapes exist: a list page that links to detail pages
  (like Kuveyt Türk), or all campaigns on one page (like T.O.M.).

## How it works, step by step

1. On a schedule (or when you press **Toplama**), each bank's scraper runs.
2. It fetches the campaign pages and pulls the campaign text out of the
   HTML using a selector we found by inspecting that bank's site once.
3. A **self-check** runs on every result: is the text suspiciously short?
   Suspiciously huge? Did the page 404? Did the selector find nothing?
4. Good results are saved as a new **snapshot** in the database. Bad
   results are saved too, but *flagged as failed* — and the system keeps
   using the last known-good snapshot for that page ("stale bank data" is
   shown honestly rather than showing nothing).

## Why this way

- **Batch on a schedule, never live-scraping while a user waits** — bank
  campaigns change maybe weekly; scraping is slow and can fail. So we
  collect in the background and users always read from our database.
- **Websites WILL break our scrapers.** We assumed this from day one. It
  already happened in real life: two Kuveyt Türk pages 404'd two days after
  we built the scraper — the self-check caught both, kept the old
  snapshots, and the system carried on.

## If someone asks…

- *"How do you handle 10 different websites?"* — "One small scraper per
  bank, each found manually once. Two page shapes cover all of them."
- *"What if a site changes?"* — "The self-check flags it, we keep the last
  good copy, and the monitor shows the failure. Nothing breaks silently."
- *"Why not scrape live when the user asks?"* — "Too slow, too fragile, and
  unnecessary — campaigns change weekly, not per second."
