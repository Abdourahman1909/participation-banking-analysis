"""Per-bank scraper base class.

See docs/adr/0001, 0002, 0010: one hand-mapped scraper per bank, fetcher
tiering (cheap HTTP first, escalate only if needed), and a self-check that
flags anomalies instead of trusting the page to look the way we expect.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from scrapling.fetchers import Fetcher


@dataclass
class CollectionResult:
    bank: str
    url: str
    fetched_at: datetime
    ok: bool
    text: str | None = None
    failure_reason: str | None = None


@dataclass
class SelfCheckConfig:
    """Structural anomaly thresholds only (ADR 0010) — not every legitimate
    campaign mentions a rate/amount, so content-marker checks belong in
    extraction's nullable fields (ADR 0014), not here.
    """

    min_length: int = 200
    max_length: int = 20_000


class BankScraper:
    """Override per bank: ``name``, ``base_url``, ``CONTENT_SELECTOR``,
    ``list_campaign_urls()``, and ``self_check_config`` if the defaults
    don't fit. ``fetcher`` defaults to the cheapest tier (plain HTTP) per
    ADR 0002's amendment — only override with DynamicFetcher/StealthyFetcher
    on the specific banks that actually need JS rendering or hit anti-bot
    protection.

    Two page shapes exist in practice (confirmed by hand against real bank
    sites, not assumed): some banks list URLs that each lead to one
    campaign's own page (override ``list_campaign_urls`` — the default
    ``run()`` handles fetching each); others put several campaigns inline
    on a single listing page (override ``run()`` directly, building
    results with ``_make_result()`` to reuse the same self-check).
    """

    name: str
    base_url: str
    CONTENT_SELECTOR: str
    fetcher = Fetcher
    is_digital: bool = False
    self_check_config: SelfCheckConfig = SelfCheckConfig()

    def list_campaign_urls(self) -> list[str]:
        raise NotImplementedError

    def run(self) -> list[CollectionResult]:
        return [self.fetch_campaign(url) for url in self.list_campaign_urls()]

    def fetch_campaign(self, url: str) -> CollectionResult:
        fetched_at = datetime.now(timezone.utc)
        try:
            response = self.fetcher.get(url, timeout=20)
        except Exception as exc:  # network/timeout/etc — a failed run, not a crash
            return CollectionResult(
                bank=self.name, url=url, fetched_at=fetched_at,
                ok=False, failure_reason=f"fetch error: {exc}",
            )

        if response.status != 200:
            return CollectionResult(
                bank=self.name, url=url, fetched_at=fetched_at,
                ok=False, failure_reason=f"HTTP {response.status}",
            )

        nodes = response.css(self.CONTENT_SELECTOR)
        if not nodes:
            return CollectionResult(
                bank=self.name, url=url, fetched_at=fetched_at, ok=False,
                failure_reason=f"selector '{self.CONTENT_SELECTOR}' matched nothing",
            )

        text = nodes[0].get_all_text(separator="\n").strip()
        return self._make_result(url, fetched_at, text)

    def _make_result(self, url: str, fetched_at: datetime, text: str) -> CollectionResult:
        ok, reason = self._self_check(text)
        return CollectionResult(
            bank=self.name, url=url, fetched_at=fetched_at,
            ok=ok, text=text if ok else None, failure_reason=reason,
        )

    def _self_check(self, text: str) -> tuple[bool, str | None]:
        cfg = self.self_check_config
        if not text:
            return False, "empty extraction"
        if len(text) < cfg.min_length:
            return False, f"too short ({len(text)} chars < {cfg.min_length})"
        if len(text) > cfg.max_length:
            return False, f"too long ({len(text)} chars > {cfg.max_length}) — likely wrong element"
        return True, None
