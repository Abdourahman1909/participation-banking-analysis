"""Operator control panel (ADR 0018). Run on its own port:

    uv run streamlit run src/banking_analysis/control_panel/app.py --server.port 8502

Control the pipeline with buttons; inspect data with the browser + read-only
SQL. Separate from the public dashboard (ADR 0012) — operator audience.
"""

from __future__ import annotations

from datetime import timedelta, timezone

import streamlit as st

from banking_analysis.control_panel import ops
from banking_analysis.frontend import theme

TR = timezone(timedelta(hours=3))

st.set_page_config(page_title="Kontrol Paneli", page_icon="⚙", layout="wide")
theme.inject_theme()

theme.html(
    """
    <div class="kc-header">
      <div class="kc-brand">
        <div class="kc-mark"></div>
        <div>
          <div class="kc-wordmark">Kontrol Paneli</div>
          <div class="kc-tagline">Boru hattını çalıştır · durumu izle · veriyi incele (operatör)</div>
        </div>
      </div>
    </div>
    """
)

durum, calistir, veri, sql = st.tabs(["  Durum  ", "  Çalıştır  ", "  Veri  ", "  SQL  "])


# ---- Durum (status) ------------------------------------------------------
with durum:
    s = ops.status()
    if not s:
        theme.html('<div class="kc-note"><h4>Veri tabanına ulaşılamadı</h4>'
                   '<p>Postgres kapalı olabilir: <code>docker compose up postgres -d</code></p></div>')
    else:
        reachable, model_info = ops.model_status()
        badge = theme.badge("ok", "bağlı", "✓") if reachable else theme.badge("stale", "kapalı", "⏱")
        theme.html(f'<div class="kc-note"><h4>Model sunucusu {badge}</h4>'
                   f'<p>{theme.esc(model_info)}</p></div>')

        c = st.columns(5)
        c[0].metric("Banka", s["banks"])
        c[1].metric("Toplanan", s["collected"])
        c[2].metric("Çıkarılan", s["extracted"])
        c[3].metric("Doğrulanan", s["validated"])
        c[4].metric("Taranan banka", f'{s["scraped_banks"]}/{s["banks"]}')

        last = s["last_collection"]
        last_str = last.astimezone(TR).strftime("%d.%m.%Y %H:%M") if last else "—"
        theme.html(
            f'<div class="kc-section-sub">Boru hattı (güncel): '
            f'<b>{s["collected"]}</b> kampanya → <b>{s["extracted"]}</b> çıkarıldı → '
            f'<b>{s["validated"]}</b> doğrulandı &nbsp;·&nbsp; '
            f'Son toplama: {theme.esc(last_str)} &nbsp;·&nbsp; '
            f'geçmiş: {s["runs_total"]} çalıştırma kaydı</div>'
        )


# ---- Çalıştır (run) ------------------------------------------------------
with calistir:
    st.markdown("#### Boru hattı adımlarını çalıştır")
    theme.html('<div class="kc-section-sub">Her düğme ilgili katmanı çalıştırır. '
               'Çıkarım ve değerlendirme için model sunucusu açık olmalı.</div>')

    steps = [
        ("collection", "▶ Toplama (scraper)", "Bankalardan kampanya metnini toplar."),
        ("extraction", "▶ Çıkarım (LLM)", "Ham metinden alanları çıkarır — model gerekir."),
        ("validation", "▶ Doğrulama", "Çıkarılan alanları kurallarla doğrular."),
        ("eval", "▶ Değerlendirme (doğruluk)", "Gerçek metinlerde doğruluğu ölçer — model gerekir."),
    ]
    for key, label, desc in steps:
        col1, col2 = st.columns([1, 2])
        if col1.button(label, key=f"run_{key}", use_container_width=True):
            with st.spinner(f"{label} çalışıyor…"):
                ok, output = ops.run_step(key)
            (st.success if ok else st.error)(f"{label}: {'tamam' if ok else 'hata'}")
            with st.expander("Çıktı", expanded=not ok):
                st.code(output)
        col2.caption(desc)


# ---- Veri (data browser) -------------------------------------------------
with veri:
    table = st.selectbox("Tablo", ops.table_names())
    try:
        cols, rows = ops.browse_table(table)
        st.caption(f"{len(rows)} satır")
        st.dataframe(ops.as_records(cols, rows), use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error(f"Okunamadı: {exc}")


# ---- SQL (read-only) -----------------------------------------------------
with sql:
    theme.html('<div class="kc-section-sub">Salt-okunur SQL — yalnızca SELECT. '
               'Veriyi değiştirmek için "Çalıştır" sekmesindeki düğmeleri kullanın (ADR 0017).</div>')
    examples = {
        "Bankalar": "SELECT name, is_digital FROM banks ORDER BY is_digital, name",
        "Toplama / banka": (
            "SELECT b.name, count(*) AS kampanya\n"
            "FROM collection_runs cr JOIN banks b ON b.id = cr.bank_id\n"
            "WHERE cr.ok GROUP BY b.name ORDER BY kampanya DESC"
        ),
        "Bir kampanyanın ham metni": (
            "SELECT url, left(raw_text, 400) AS onizleme\n"
            "FROM collection_runs WHERE ok LIMIT 1"
        ),
    }
    cols = st.columns(len(examples))
    if "sql_text" not in st.session_state:
        st.session_state.sql_text = examples["Bankalar"]
    for i, (lbl, q) in enumerate(examples.items()):
        if cols[i].button(lbl, key=f"ex_{i}", use_container_width=True):
            st.session_state.sql_text = q

    query = st.text_area("Sorgu", key="sql_text", height=130)
    if st.button("Çalıştır", type="primary"):
        try:
            cols_, rows_ = ops.read_only_sql(query)
            st.caption(f"{len(rows_)} satır")
            st.dataframe(ops.as_records(cols_, rows_), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(str(exc))
