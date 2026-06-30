"""Layer 6 — Frontend (ADR 0012, 0009). Strategic brief: PRODUCT.md.
Visual system: DESIGN.md + theme.py.

Two views behind a clean read-only boundary over the Knowledge Store
(Layer 4): a cross-bank comparison **Panel** and a **Sohbet** (chatbot).
Real bank list + collection stats come from Postgres; extracted product
fields use illustrative sample data (sample_data.py) until Layer 2 runs,
always badged as preview so nothing fake is shown as confirmed.
"""

from __future__ import annotations

import streamlit as st

from banking_analysis.frontend import theme
from banking_analysis.frontend.sample_data import (
    CAMPAIGN_TYPE_LABELS,
    Campaign,
    sample_campaigns,
    type_label,
)

st.set_page_config(page_title="Katılım Compare", page_icon="◆", layout="wide")
theme.inject_theme()


# --------------------------------------------------------------------------
# Data access (Layer 4). Defensive: the UI must never crash if Postgres is
# down — it degrades to sample data with the stats shown as unavailable.
# --------------------------------------------------------------------------
@st.cache_data(ttl=60)
def db_stats() -> dict | None:
    try:
        from banking_analysis.storage.db import connect

        with connect() as conn:
            banks = conn.execute("SELECT count(*) FROM banks").fetchone()[0]
            runs = conn.execute(
                "SELECT count(*) FROM collection_runs WHERE ok = TRUE"
            ).fetchone()[0]
            last = conn.execute(
                "SELECT max(fetched_at) FROM collection_runs WHERE ok = TRUE"
            ).fetchone()[0]
        return {"banks": banks, "campaigns": runs, "last": last}
    except Exception:
        return None


@st.cache_data(ttl=60)
def load_campaigns() -> tuple[list[Campaign], bool]:
    """Real extracted campaigns from the DB if Layer 2 has populated them,
    otherwise the illustrative sample set. Returns (rows, is_sample)."""
    try:
        from banking_analysis.storage.db import connect

        with connect() as conn:
            n = conn.execute("SELECT count(*) FROM campaigns").fetchone()[0]
            if n == 0:
                return sample_campaigns(), True
            rows = conn.execute(
                """
                SELECT b.name, c.title, c.campaign_type,
                       max(f.value) FILTER (WHERE f.field_name = 'profit_share_rate'),
                       max(f.value) FILTER (WHERE f.field_name = 'maturity_months'),
                       max(f.value) FILTER (WHERE f.field_name = 'cost_amount'),
                       max(f.evidence_quote) FILTER (WHERE f.field_name = 'profit_share_rate'),
                       bool_and(coalesce(f.is_valid, TRUE))
                FROM campaigns c
                JOIN banks b ON b.id = c.bank_id
                LEFT JOIN campaign_fields f ON f.campaign_id = c.id
                WHERE c.is_no_campaign = FALSE
                GROUP BY b.name, c.title, c.campaign_type
                """
            ).fetchall()
        out = [
            Campaign(
                bank=r[0], title=r[1] or "—", ctype=r[2] or "other",
                profit_rate=r[3], rate_sort=_parse_rate(r[3]),
                term_months=int(r[4]) if r[4] and str(r[4]).isdigit() else None,
                amount=r[5], evidence=r[6] or "", valid=bool(r[7]),
            )
            for r in rows
        ]
        return out, False
    except Exception:
        return sample_campaigns(), True


def _parse_rate(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.replace("%", "").replace(",", ".").strip().split()[0]
    try:
        return float(cleaned)
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
def render_header(stats: dict | None) -> None:
    if stats:
        last = stats["last"]
        last_str = last.strftime("%d.%m.%Y") if last else "—"
        right = (
            f'<b>{stats["banks"]}</b> banka &nbsp;·&nbsp; '
            f'<b>{stats["campaigns"]}</b> kampanya &nbsp;·&nbsp; '
            f'<b>8</b> ürün tipi<br>Son toplama: {theme.esc(last_str)} '
            f'&nbsp;·&nbsp; çevrimdışı'
        )
    else:
        right = (
            'Veri tabanı kapalı &nbsp;·&nbsp; örnek veri gösteriliyor<br>'
            '<span style="opacity:.7">docker compose up postgres</span>'
        )
    theme.html(
        f"""
        <div class="kc-header">
          <div class="kc-brand">
            <div class="kc-mark"></div>
            <div>
              <div class="kc-wordmark">Katılım&nbsp;Compare</div>
              <div class="kc-tagline">Türkiye katılım bankalarının ürünlerini tek yerde karşılaştırın</div>
            </div>
          </div>
          <div class="kc-stats kc-num">{right}</div>
        </div>
        """
    )


# --------------------------------------------------------------------------
# Comparison table
# --------------------------------------------------------------------------
def render_table(rows: list[Campaign], highlight_best: bool) -> None:
    best_rate = None
    if highlight_best:
        rates = [r.rate_sort for r in rows if r.rate_sort is not None]
        best_rate = min(rates) if rates else None

    body = []
    for r in rows:
        is_best = best_rate is not None and r.rate_sort == best_rate
        rate_cell = (
            f'<span class="kc-null">—</span>' if r.profit_rate is None
            else theme.esc(r.profit_rate)
        )
        if is_best:
            rate_cell += '<span class="kc-best-tag">EN DÜŞÜK</span>'
        term_cell = (
            f'<span class="kc-null">—</span>' if r.term_months is None
            else f"{r.term_months} ay"
        )
        amount_cell = (
            f'<span class="kc-null">—</span>' if r.amount is None
            else theme.esc(r.amount)
        )
        src = theme.esc(r.evidence)
        src_cell = (
            f'<span class="kc-src" title="{src}">❝ {src[:34]}'
            f'{"…" if len(r.evidence) > 34 else ""}</span>'
        )
        row_cls = " kc-row--best" if is_best else ""
        body.append(
            f"""
            <tr class="{row_cls.strip()}">
              <td class="kc-bank"><span class="kc-bank-row">
                  <span class="kc-dot"></span>{theme.esc(r.bank)}</span></td>
              <td class="kc-camp">{theme.esc(r.title)}</td>
              <td>{theme.chip(type_label(r.ctype))}</td>
              <td class="kc-data">{rate_cell}</td>
              <td class="kc-data">{term_cell}</td>
              <td class="kc-data">{amount_cell}</td>
              <td>{src_cell}</td>
            </tr>
            """
        )

    theme.html(
        f"""
        <div class="kc-table-wrap"><table class="kc-table">
        <thead><tr>
        <th>Banka</th><th>Kampanya</th><th>Tür</th>
        <th>Kâr Payı (aylık)</th><th>Vade</th><th>Tutar</th><th>Kaynak</th>
        </tr></thead>
        <tbody>{"".join(body)}</tbody>
        </table></div>
        """
    )


def view_panel() -> None:
    rows, is_sample = load_campaigns()

    if is_sample:
        theme.html(
            f"""
            <div class="kc-note">
            <h4>{theme.badge("preview", "Önizleme — örnek veriler", "◆")} &nbsp; Çıkarım katmanı henüz çalışmadı</h4>
            <p>Aşağıdaki ürün alanları (kâr payı, vade, tutar) örnek verilerdir. Gerçek değerler, yerel LLM (Qwen2.5) ham kampanya metnini işleyince otomatik olarak veritabanından gelecek — kod değişmeden. Banka listesi ve toplama sayıları gerçektir.</p>
            </div>
            """
        )

    types_present = sorted(
        {r.ctype for r in rows}, key=lambda t: CAMPAIGN_TYPE_LABELS.get(t, t)
    )
    type_options = ["Tümü"] + [type_label(t) for t in types_present]
    label_to_key = {type_label(t): t for t in types_present}

    c1, c2, _ = st.columns([1.2, 1.2, 1.6])
    with c1:
        sel_type = st.selectbox("Ürün tipi", type_options, index=0)
    with c2:
        sort = st.selectbox(
            "Sırala",
            ["Önerilen", "Kâr payı (artan)", "Kâr payı (azalan)",
             "Vade (artan)", "Banka (A–Z)"],
            index=0,
        )

    single_type = sel_type != "Tümü"
    if single_type:
        key = label_to_key[sel_type]
        rows = [r for r in rows if r.ctype == key]

    big = float("inf")
    if sort == "Kâr payı (artan)":
        rows.sort(key=lambda r: (r.rate_sort is None, r.rate_sort or big))
    elif sort == "Kâr payı (azalan)":
        rows.sort(key=lambda r: (r.rate_sort is None, -(r.rate_sort or 0)))
    elif sort == "Vade (artan)":
        rows.sort(key=lambda r: (r.term_months is None, r.term_months or 10**9))
    elif sort == "Banka (A–Z)":
        rows.sort(key=lambda r: r.bank.lower())
    else:  # Önerilen — group by type, then cheapest rate first
        rows.sort(key=lambda r: (
            type_label(r.ctype), r.rate_sort is None, r.rate_sort or big))

    note = " · en düşük kâr payı işaretli" if single_type else ""
    theme.html(f'<div class="kc-section-sub">{len(rows)} kampanya{note}</div>')
    # Best-value highlight only within a single product type — comparing
    # rates across different product types would be misleading (PRODUCT.md).
    render_table(rows, highlight_best=single_type)


# --------------------------------------------------------------------------
# Chat (ADR 0007 agent / ADR 0009 answer+sources contract)
# --------------------------------------------------------------------------
def _canned_answer(question: str) -> dict:
    q = question.lower()
    rows = sample_campaigns()

    def best_of(ctype: str) -> Campaign:
        cands = [r for r in rows if r.ctype == ctype and r.rate_sort]
        return min(cands, key=lambda r: r.rate_sort)

    if "konut" in q or "ev" in q or "mortgage" in q:
        b = best_of("housing_finance")
        ans = (f"Şu anki örnek verilere göre en düşük konut finansmanı kâr "
               f"payı **{b.bank}**’ta: aylık **{b.profit_rate}**, "
               f"{b.term_months} ay vadeye kadar.")
        srcs = [b]
    elif "taşıt" in q or "araç" in q or "araba" in q:
        b = best_of("vehicle_financing")
        ans = (f"En uygun taşıt finansmanı örnek verilerde **{b.bank}**’ta: "
               f"aylık kâr payı **{b.profit_rate}**, {b.term_months} ay.")
        srcs = [b]
    else:
        ans = ("Örnek verilerde en düşük kâr payı oranları taşıt ve konut "
               "finansmanında. Belirli bir ürün tipi sorab[i]lirsiniz "
               "(ör. “en uygun konut finansmanı hangi bankada?”).")
        srcs = [best_of("vehicle_financing"), best_of("housing_finance")]
    return {"answer": ans, "sources": srcs}


def render_sources(sources: list[Campaign]) -> str:
    items = "".join(
        f'<div class="kc-source-item"><b>{theme.esc(s.bank)}</b> — '
        f'{theme.esc(s.title)}<br><em>“{theme.esc(s.evidence)}”</em></div>'
        for s in sources
    )
    return f'<div class="kc-sources"><div class="kc-src-head">Kaynaklar</div>{items}</div>'


def view_chat() -> None:
    theme.html(
        f"""
        <div class="kc-note">
        <h4>{theme.badge("preview", "Önizleme sohbeti", "◆")} &nbsp; Akıl yürütme katmanı (agent) henüz bağlanmadı</h4>
        <p>Aşağıdaki yanıtlar örnek verilerden üretilen hazır cevaplardır ve <b>cevap + kaynak</b> sözleşmesini (ADR 0009) gösterir. Gerçek sohbet, yerel LLM tool-calling agent (ADR 0007) devreye girince aynı biçimde — her cevabın altında kanıt cümleleriyle — çalışacak.</p>
        </div>
        """
    )

    if "chat" not in st.session_state:
        st.session_state.chat = [
            {"role": "assistant",
             "answer": "Merhaba 👋 Katılım bankalarının kampanyalarını "
                       "karşılaştırmak için sorun: örn. “en uygun taşıt "
                       "finansmanı hangi bankada?”",
             "sources": []},
        ]

    # Explicit emoji avatars: Streamlit's default avatars use a Material-icon
    # font that won't load in the offline deployment (CLAUDE.md), rendering
    # the ligature name ("smart_toy") as text instead of a glyph.
    avatars = {"user": "🧑", "assistant": "💠"}
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"], avatar=avatars[msg["role"]]):
            st.markdown(msg["answer"])
            if msg.get("sources"):
                theme.html(render_sources(msg["sources"]))

    if prompt := st.chat_input("Bir soru sorun…"):
        st.session_state.chat.append(
            {"role": "user", "answer": prompt, "sources": []})
        result = _canned_answer(prompt)
        st.session_state.chat.append(
            {"role": "assistant", "answer": result["answer"],
             "sources": result["sources"]})
        st.rerun()


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------
render_header(db_stats())
panel, chat = st.tabs(["  Panel  ", "  Sohbet  "])
with panel:
    view_panel()
with chat:
    view_chat()
