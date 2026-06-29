"""Layer 6 — Frontend. See docs/adr/0012, 0009.

Placeholder dashboard. Real comparison table/chatbot land once Layer 2
(extraction, ADR 0004) and Layer 5 (agent, ADR 0007) exist — for now this
just proves the app container can read the Knowledge Store (Layer 4).
"""

import streamlit as st

from banking_analysis.storage.db import connect

st.set_page_config(page_title="Participation Banking Analysis", layout="wide")
st.title("Participation Banking Product Analysis")
st.caption("TEKNOFEST 2026 — Scenario 2")

try:
    with connect() as conn:
        banks = conn.execute("SELECT name, website, is_digital FROM banks ORDER BY name").fetchall()
    if banks:
        st.subheader(f"Tracked banks ({len(banks)})")
        st.table(
            [{"Bank": b[0], "Website": b[1], "Digital-only": b[2]} for b in banks]
        )
    else:
        st.info("No banks in the Knowledge Store yet — run the scheduler's collection job first.")
except Exception as exc:
    st.error(f"Could not reach the Knowledge Store: {exc}")

st.divider()
st.caption("Comparison dashboard and chatbot pending the extraction and agent layers.")
