"""Operator control panel (ADR 0018) — a cross-cutting ops console, NOT a
pipeline layer. Wraps the layer runners with buttons, shows pipeline status,
and offers a data browser + read-only SQL. Run on its own port:

    uv run streamlit run src/banking_analysis/control_panel/app.py --server.port 8502
"""
