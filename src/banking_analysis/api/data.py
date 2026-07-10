"""Data endpoints' logic (ADR 0022): stats, campaigns, chat. UI-free.

Mirrors the behavior of frontend/dashboard.py exactly — same queries, same
graceful degradation: if Postgres is down or extraction hasn't run, campaigns
fall back to the illustrative sample set flagged `is_sample` so no client can
show fake data as confirmed (PRODUCT.md principle 4).
"""

from __future__ import annotations

from banking_analysis.agent.models import Source
from banking_analysis.api.schemas import (
    CampaignItem,
    CampaignList,
    ChatResponse,
    Stats,
)
from banking_analysis.frontend.sample_data import Campaign, sample_campaigns

# Same Current View queries as the dashboard header (ADR 0017).
_STATS_CAMPAIGNS = (
    "SELECT count(*) FROM (SELECT DISTINCT bank_id, url "
    "FROM collection_runs WHERE ok = TRUE) t"
)
_STATS_LAST = "SELECT max(fetched_at) FROM collection_runs WHERE ok = TRUE"

# Same aggregation the dashboard uses: one row per campaign, fields pivoted,
# sortable values from value_normalized (ADR 0008/0017 — never re-parse).
_CAMPAIGNS_SQL = """
    SELECT b.name, c.title, c.campaign_type,
           max(f.value) FILTER (WHERE f.field_name = 'profit_share_rate'),
           max(f.value) FILTER (WHERE f.field_name = 'maturity_months'),
           max(f.value) FILTER (WHERE f.field_name = 'cost_amount'),
           max(f.evidence_quote) FILTER (WHERE f.field_name = 'profit_share_rate'),
           bool_and(coalesce(f.is_valid, TRUE)),
           max(f.value_normalized) FILTER (WHERE f.field_name = 'profit_share_rate'),
           max(f.value_normalized) FILTER (WHERE f.field_name = 'maturity_months')
    FROM campaigns c
    JOIN banks b ON b.id = c.bank_id
    LEFT JOIN campaign_fields f ON f.campaign_id = c.id
    WHERE c.is_no_campaign = FALSE
    GROUP BY b.name, c.title, c.campaign_type
"""


def get_stats() -> Stats:
    try:
        from banking_analysis.storage.db import connect

        with connect() as conn:
            banks = conn.execute("SELECT count(*) FROM banks").fetchone()[0]
            campaigns = conn.execute(_STATS_CAMPAIGNS).fetchone()[0]
            last = conn.execute(_STATS_LAST).fetchone()[0]
        return Stats(banks=banks, campaigns=campaigns, last_collection=last)
    except Exception:
        return Stats(db_ok=False)


def _from_sample(c: Campaign) -> CampaignItem:
    return CampaignItem(
        bank=c.bank, title=c.title, campaign_type=c.ctype,
        profit_share_rate=c.profit_rate,
        maturity_months=str(c.term_months) if c.term_months is not None else None,
        cost_amount=c.amount, evidence_quote=c.evidence,
        rate_normalized=c.rate_sort, term_months=c.term_months,
        is_valid=c.valid,
    )


def get_campaigns(campaign_type: str | None = None) -> CampaignList:
    try:
        from banking_analysis.storage.db import connect

        with connect() as conn:
            n = conn.execute("SELECT count(*) FROM campaigns").fetchone()[0]
            if n == 0:
                raise LookupError("extraction has not populated campaigns yet")
            rows = conn.execute(_CAMPAIGNS_SQL).fetchall()
        items = [
            CampaignItem(
                bank=r[0], title=r[1] or "—", campaign_type=r[2] or "other",
                profit_share_rate=r[3], maturity_months=r[4], cost_amount=r[5],
                evidence_quote=r[6] or "", is_valid=bool(r[7]),
                rate_normalized=float(r[8]) if r[8] is not None else None,
                term_months=int(r[9]) if r[9] is not None else None,
            )
            for r in rows
        ]
        is_sample = False
    except Exception:
        items = [_from_sample(c) for c in sample_campaigns()]
        is_sample = True

    if campaign_type:
        items = [i for i in items if i.campaign_type == campaign_type]
    return CampaignList(items=items, is_sample=is_sample)


# ---------------------------------------------------------------------------
# Chat (ADR 0007 agent / ADR 0009 answer+sources). Same fallback ladder as
# the dashboard: real agent when campaigns exist AND the model answers,
# otherwise the canned preview — always flagged is_preview.
# ---------------------------------------------------------------------------
def _source_from(c: Campaign) -> Source:
    return Source(
        bank=c.bank, title=c.title, field="profit_share_rate",
        value=c.profit_rate, evidence_quote=c.evidence,
    )


def _canned_answer(question: str) -> ChatResponse:
    q = question.lower()
    rows = sample_campaigns()

    def best_of(ctype: str) -> Campaign:
        cands = [r for r in rows if r.ctype == ctype and r.rate_sort]
        return min(cands, key=lambda r: r.rate_sort)

    if "konut" in q or "ev" in q or "mortgage" in q:
        b = best_of("housing_finance")
        ans = (f"Şu anki örnek verilere göre en düşük konut finansmanı kâr "
               f"payı **{b.bank}**'ta: aylık **{b.profit_rate}**, "
               f"{b.term_months} ay vadeye kadar.")
        srcs = [b]
    elif "taşıt" in q or "araç" in q or "araba" in q:
        b = best_of("vehicle_financing")
        ans = (f"En uygun taşıt finansmanı örnek verilerde **{b.bank}**'ta: "
               f"aylık kâr payı **{b.profit_rate}**, {b.term_months} ay.")
        srcs = [b]
    else:
        ans = ("Örnek verilerde en düşük kâr payı oranları taşıt ve konut "
               "finansmanında. Belirli bir ürün tipi sorabilirsiniz "
               "(ör. “en uygun konut finansmanı hangi bankada?”).")
        srcs = [best_of("vehicle_financing"), best_of("housing_finance")]
    return ChatResponse(
        answer=ans, sources=[_source_from(b) for b in srcs], is_preview=True,
    )


def get_answer(question: str) -> ChatResponse:
    try:
        from banking_analysis.agent.agent import answer as agent_answer
        from banking_analysis.extraction.client import get_model
        from banking_analysis.storage.db import connect

        with connect() as conn:
            has_data = conn.execute("SELECT count(*) FROM campaigns").fetchone()[0]
            if has_data:
                res = agent_answer(question, get_model(), conn)
                return ChatResponse(answer=res.answer, sources=res.sources)
    except Exception:
        pass
    return _canned_answer(question)
