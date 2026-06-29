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
