from banking_analysis.collection.base import BankScraper, SelfCheckConfig

CAMPAIGN_LIST_PAGES = (
    "https://www.kuveytturk.com.tr/kampanyalar/kendim-icin",
)


class KuveytTurkScraper(BankScraper):
    name = "Kuveyt Türk Katılım Bankası"
    base_url = "https://www.kuveytturk.com.tr"
    CONTENT_SELECTOR = ".campaign-detail"
    # Not every legitimate campaign states a numeric rate (e.g. an
    # interest-free-installment or favorable-FX campaign may not) — that's
    # an extraction-time nullable field (ADR 0014), not a scraping anomaly.
    # Self-check here only catches "wrong element" structurally: empty or
    # drastically mis-sized output.
    self_check_config = SelfCheckConfig(min_length=150, max_length=20_000)

    def list_campaign_urls(self) -> list[str]:
        urls: set[str] = set()
        for list_url in CAMPAIGN_LIST_PAGES:
            response = self.fetcher.get(list_url, timeout=20)
            for href in response.css("a::attr(href)").getall():
                if href and "/kampanyalar/kendim-icin/" in href:
                    urls.add(self._absolute(href))
        return sorted(urls)

    def _absolute(self, href: str) -> str:
        if href.startswith("http"):
            return href.split("?")[0]
        return self.base_url + href.split("?")[0]
