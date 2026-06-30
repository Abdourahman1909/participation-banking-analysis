"""Layer 6 — illustrative extracted campaigns, used ONLY until Layer 2
(extraction, ADR 0004) populates the real `campaigns` / `campaign_fields`
tables. The dashboard tries the database first and falls back to this.

Honesty (PRODUCT.md principle 4): the dashboard always badges this as
preview/sample data. Rows marked ``real=True`` mirror values actually seen
in the live-scraped text now sitting in ``collection_runs`` (Kuveyt Türk);
the rest are plausible placeholders to show cross-bank comparison working.
Nothing here is presented to the user as confirmed bank data.
"""

from __future__ import annotations

from dataclasses import dataclass

# campaign_type enum (db/schema.sql, ADR 0011) -> Turkish display label.
CAMPAIGN_TYPE_LABELS: dict[str, str] = {
    "funding": "Katılım Fonu",
    "personal_financing": "Bireysel Finansman",
    "housing_finance": "Konut Finansmanı",
    "vehicle_financing": "Taşıt Finansmanı",
    "card": "Kart",
    "shopping_points": "Alışveriş Puanı",
    "new_customer": "Yeni Müşteri",
    "investment_product": "Yatırım Ürünü",
    "other": "Diğer",
}


@dataclass(frozen=True)
class Campaign:
    bank: str            # short display name
    title: str
    ctype: str           # campaign_type enum key
    profit_rate: str | None      # display, e.g. "%2,96" (aylık kâr payı)
    rate_sort: float | None      # numeric monthly rate, for sort/best-value
    term_months: int | None
    amount: str | None           # display, e.g. "300.000 TL"
    evidence: str                # the source sentence (ADR 0004 evidence quote)
    valid: bool = True           # rule-based validation flag (ADR 0008)
    real: bool = False           # True = value mirrors actual scraped text


# real=True rows reflect text actually scraped from kuveytturk.com.tr and now
# stored in collection_runs (see the raw_text we read this session).
_SAMPLE: list[Campaign] = [
    # ---- Taşıt Finansmanı (vehicle) — comparable monthly profit rates ----
    Campaign("Türkiye Finans", "Taşıt Finansmanında Avantajlı Dönem",
             "vehicle_financing", "%2,89", 2.89, 12, "250.000 TL",
             "Taşıt finansmanında aylık kâr payı oranı %2,89'dan başlıyor."),
    Campaign("Kuveyt Türk", "Yeni Müşterilere Dijital Araç Finansmanı İndirimi",
             "vehicle_financing", "%2,96", 2.96, 12, "300.000 TL",
             "Örnek: 300.000 TL, 12 ay, aylık kâr oranı %2,96.", real=True),
    Campaign("Albaraka", "Taşıt Finansmanı Kampanyası",
             "vehicle_financing", "%3,10", 3.10, 24, "400.000 TL",
             "24 aya varan vadede aylık %3,10 kâr payı ile taşıt finansmanı."),
    Campaign("Ziraat Katılım", "Araç Finansmanı Fırsatı",
             "vehicle_financing", "%3,25", 3.25, 36, "500.000 TL",
             "36 ay vade ile aylık kâr payı oranı %3,25."),

    # ---- Konut Finansmanı (housing) ----
    Campaign("Emlak Katılım", "Konut Finansmanında İndirimli Dönem",
             "housing_finance", "%2,39", 2.39, 120, "2.000.000 TL",
             "Konut finansmanında aylık kâr payı oranı %2,39."),
    Campaign("Vakıf Katılım", "Ev Sahibi Olma Kampanyası",
             "housing_finance", "%2,45", 2.45, 120, "1.750.000 TL",
             "120 aya varan vade, aylık %2,45 kâr payı."),
    Campaign("Albaraka", "Konut Finansmanı",
             "housing_finance", "%2,55", 2.55, 60, "1.500.000 TL",
             "60 ay vade ile aylık kâr payı %2,55'ten başlayan konut finansmanı."),

    # ---- Bireysel Finansman (personal) ----
    Campaign("Türkiye Finans", "Bireysel Finansman Desteği",
             "personal_financing", "%3,49", 3.49, 24, "150.000 TL",
             "Bireysel finansmanda 24 ay vade, aylık kâr payı %3,49."),

    # ---- Kart (card) — rate genuinely null (ADR 0014 nullable field) ----
    Campaign("Kuveyt Türk", "Civil'de Vade Farksız 4 Aya Varan Taksit",
             "card", None, None, 4, None,
             "Civil resmi web sitesinde vade farksız 4 aya varan taksit imkanı.",
             real=True),
    Campaign("Kuveyt Türk", "Eğitim ve Sağlık Harcamalarında 5 Taksit",
             "card", None, None, 5, None,
             "Eğitim ve sağlık harcamalarınızda 5 taksit fırsatı.", real=True),

    # ---- Yeni Müşteri (new customer) — gift amounts, no rate ----
    Campaign("Kuveyt Türk", "Babalar Günü Hediyesi",
             "new_customer", None, None, None, "1.000 TL",
             "Babalar Günü hediyenize 1.000 TL nakit iade.", real=True),
    Campaign("Kuveyt Türk", "Kampüse Gelenlere Hediye",
             "new_customer", None, None, None, "13.500 TL",
             "Kuveyt Türk'lü kampüs öğrencilerine toplamda 13.500 TL hediye.",
             real=True),
    Campaign("Hayat Finans", "Yeni Dijital Müşteri Hediyesi",
             "new_customer", None, None, None, "750 TL",
             "Mobilden yeni müşteri olanlara 750 TL hoş geldin hediyesi."),
    Campaign("T.O.M.", "Mobil Müşteri Kampanyası",
             "new_customer", None, None, None, "500 TL",
             "T.O.M. mobil uygulamasından müşteri olanlara 500 TL hediye."),
]


def sample_campaigns() -> list[Campaign]:
    return list(_SAMPLE)


def type_label(ctype: str | None) -> str:
    if not ctype:
        return "—"
    return CAMPAIGN_TYPE_LABELS.get(ctype, ctype)
