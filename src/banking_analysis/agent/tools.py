"""Layer 5 — the agent's fixed, read-only toolset (ADR 0007).

Deliberately small. Every tool is a read-only query over the Knowledge Store
(Layer 4) and returns rows that include the evidence quote, so answers can be
sourced (ADR 0009). No write tool, no live-scrape tool (ADR 0003), no vector
tool (ADR 0006). Only validated values are surfaced (is_valid not false).
"""

from __future__ import annotations

import psycopg

# Pivot campaigns + their valid fields into one row per campaign.
_BASE_QUERY = """
SELECT b.name, c.title, c.campaign_type,
       max(f.value)            FILTER (WHERE f.field_name = 'profit_share_rate'),
       max(f.value_normalized) FILTER (WHERE f.field_name = 'profit_share_rate'),
       max(f.evidence_quote)   FILTER (WHERE f.field_name = 'profit_share_rate'),
       max(f.value)            FILTER (WHERE f.field_name = 'maturity_months'),
       max(f.value)            FILTER (WHERE f.field_name = 'cost_amount')
FROM campaigns c
JOIN banks b ON b.id = c.bank_id
LEFT JOIN campaign_fields f
       ON f.campaign_id = c.id AND coalesce(f.is_valid, TRUE) = TRUE
WHERE c.is_no_campaign = FALSE
"""


def _row_to_dict(r) -> dict:
    return {
        "bank": r[0],
        "title": r[1],
        "campaign_type": r[2],
        "profit_share_rate": r[3],
        "rate_numeric": float(r[4]) if r[4] is not None else None,
        "rate_evidence": r[5],
        "maturity_months": r[6],
        "cost_amount": r[7],
    }


def get_campaigns(conn: psycopg.Connection, campaign_type: str | None = None) -> list[dict]:
    """List campaigns, optionally filtered to one campaign_type."""
    sql = _BASE_QUERY
    params: tuple = ()
    if campaign_type:
        sql += " AND c.campaign_type = %s"
        params = (campaign_type,)
    sql += " GROUP BY b.name, c.title, c.campaign_type"
    return [_row_to_dict(r) for r in conn.execute(sql, params).fetchall()]


def compare_by_rate(conn: psycopg.Connection, campaign_type: str) -> list[dict]:
    """Campaigns of one type that have a profit-share rate, cheapest first —
    the basis for a 'which bank is best' recommendation."""
    rows = [r for r in get_campaigns(conn, campaign_type) if r["rate_numeric"] is not None]
    return sorted(rows, key=lambda r: r["rate_numeric"])


# Tool schemas advertised to the model (Ollama / Qwen function-calling format).
TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_campaigns",
            "description": "List participation-bank campaigns, optionally filtered "
                           "by campaign type. Use for 'what campaigns exist' questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_type": {
                        "type": "string",
                        "description": "Optional filter, e.g. vehicle_financing, "
                                       "housing_finance, card, new_customer.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_by_rate",
            "description": "Campaigns of one type sorted by profit-share rate, "
                           "cheapest first. Use to recommend the best bank for a "
                           "financing type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_type": {
                        "type": "string",
                        "description": "Required, e.g. vehicle_financing or housing_finance.",
                    }
                },
                "required": ["campaign_type"],
            },
        },
    },
]

# name -> callable(conn, **args)
TOOL_FUNCS = {
    "get_campaigns": get_campaigns,
    "compare_by_rate": compare_by_rate,
}
