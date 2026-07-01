from datetime import datetime, timezone

from banking_analysis.collection.base import BankScraper, CollectionResult, SelfCheckConfig

CAMPAIGNS_PAGE = "https://www.tombank.com.tr/kampanyalar.html"

# Title+description and terms live as non-adjacent siblings on one page —
# not separate detail pages like Kuveyt Türk. Confirmed by hand against the
# live page (2026-06-29); not assumed from the README-level "campaigns page"
# idea.
TITLE_DESC_SELECTOR = ".d-flex.flex-column-reverse.flex-lg-row"
TERMS_SELECTOR = ".accordion"


class TomBankScraper(BankScraper):
    """T.O.M. Katılım Bankası — digital-only bank, consumer brand "Hadi".
    Its corporate domain (tombank.com.tr) hosts real campaign content
    directly; the consumer brand domain (hadiyanindakibanka.com) turned out
    to be a JS-rendered search/FAQ shell our plain fetch can't read, so we
    use the corporate domain instead.
    """

    name = "T.O.M. Katılım Bankası"
    base_url = "https://www.tombank.com.tr"
    is_digital = True
    self_check_config = SelfCheckConfig(min_length=100, max_length=15_000)

    def list_campaign_urls(self) -> list[str]:
        return [CAMPAIGNS_PAGE]

    def run(self) -> list[CollectionResult]:
        fetched_at = datetime.now(timezone.utc)
        response = self.fetcher.get(CAMPAIGNS_PAGE, timeout=20)
        if response.status != 200:
            return [CollectionResult(
                bank=self.name, url=CAMPAIGNS_PAGE, fetched_at=fetched_at,
                ok=False, failure_reason=f"HTTP {response.status}",
            )]

        # First match is the whole-page wrapper (an ancestor of all cards),
        # so campaign N is cards[N+1] — confirmed against the live page.
        cards = response.css(TITLE_DESC_SELECTOR)[1:]
        terms = response.css(TERMS_SELECTOR)

        if not cards:
            return [CollectionResult(
                bank=self.name, url=CAMPAIGNS_PAGE, fetched_at=fetched_at,
                ok=False, failure_reason="no campaign cards found on listing page",
            )]

        results = []
        for i, card in enumerate(cards):
            text = card.get_all_text(separator="\n").strip()
            if i < len(terms):
                text += "\n" + terms[i].get_all_text(separator="\n").strip()
            url = f"{CAMPAIGNS_PAGE}#campaign-{i}"
            results.append(self._make_result(url, fetched_at, text))
        return results
