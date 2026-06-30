"""Layer 6 — Frontend design system (DESIGN.md).

Streamlit's base theme is set in `.streamlit/config.toml`; everything that
makes this not-look-like-default-Streamlit (typography, the comparison
table, chips, badges, chat sources, hidden chrome) is the injected CSS here.
Offline constraint (CLAUDE.md): system font stack only, no font CDN.
"""

from __future__ import annotations

import html as _stdhtml

import streamlit as st

# OKLCH palette + the full component system. Kept as one stylesheet so the
# whole visual language is in a single, auditable place.
_CSS = """
<style>
:root {
  --bg: oklch(1 0 0);
  --surface: oklch(0.985 0.004 178);
  --surface-2: oklch(0.965 0.006 178);
  --ink: oklch(0.21 0.018 195);
  --ink-muted: oklch(0.46 0.016 200);
  --border: oklch(0.9 0.006 195);
  --border-strong: oklch(0.82 0.008 195);
  --brand: oklch(0.52 0.09 178);
  --brand-hover: oklch(0.46 0.092 178);
  --brand-tint: oklch(0.95 0.03 178);
  --success: oklch(0.55 0.11 155);
  --warning: oklch(0.72 0.13 75);
  --danger: oklch(0.55 0.18 25);
  --info: oklch(0.55 0.1 240);
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Ubuntu,
          Cantarell, "Helvetica Neue", Arial, sans-serif;
  --r-input: 8px;
  --r-panel: 10px;
  --r-table: 12px;
  --ease: cubic-bezier(0.22, 1, 0.36, 1);
}

/* ---- base ---- */
html, body, [class*="st-"], .stApp, button, input, select, textarea {
  font-family: var(--font) !important;
}
.stApp { background: var(--bg); color: var(--ink); }
[data-testid="stAppViewContainer"] .block-container {
  max-width: 1100px;
  padding-top: 1.4rem;
  padding-bottom: 4rem;
}
.stApp, .stApp p, .stApp li, .stApp span, .stApp div { color: var(--ink); }
.stApp p { line-height: 1.55; }

/* ---- hide default Streamlit chrome for a product feel ---- */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { visibility: hidden; height: 0; }
[data-testid="stHeader"] { background: transparent; height: 0; }

/* ---- numbers: tabular figures so columns align ---- */
.kc-num, .kc-table td.kc-data, .kc-stats b {
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum" 1;
}

/* ---- app header ---- */
.kc-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: 1.5rem; flex-wrap: wrap;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-panel);
  padding: 0.85rem 1.15rem;
  margin-bottom: 1.4rem;
}
.kc-brand { display: flex; align-items: center; gap: 0.7rem; }
.kc-mark {
  width: 26px; height: 26px; flex: none;
  background: var(--brand);
  border-radius: 7px;
  transform: rotate(45deg);
  box-shadow: inset 0 0 0 3px oklch(1 0 0 / 0.55);
}
.kc-wordmark {
  font-size: 1.6rem; font-weight: 650; letter-spacing: -0.02em;
  line-height: 1.05;
}
.kc-tagline { color: var(--ink-muted); font-size: 0.8rem; margin-top: 1px; }
.kc-stats {
  color: var(--ink-muted); font-size: 0.84rem; text-align: right;
  line-height: 1.5;
}
.kc-stats b { color: var(--ink); font-weight: 600; }

/* ---- section header ---- */
.kc-section {
  font-size: 1.15rem; font-weight: 620; letter-spacing: -0.01em;
  margin: 0.4rem 0 0.2rem;
}
.kc-section-sub { color: var(--ink-muted); font-size: 0.85rem; margin-bottom: 0.9rem; }

/* ---- comparison table ---- */
.kc-table-wrap {
  border: 1px solid var(--border);
  border-radius: var(--r-table);
  overflow-x: auto;
  margin-top: 0.4rem;
}
.kc-table { width: 100%; border-collapse: collapse; font-size: 0.94rem; }
.kc-table thead th {
  background: var(--surface);
  color: var(--ink-muted);
  text-align: left;
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.7rem 0.9rem;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.kc-table tbody td {
  padding: 0.72rem 0.9rem;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}
.kc-table tbody tr:last-child td { border-bottom: none; }
.kc-table tbody tr { transition: background 160ms var(--ease); }
.kc-table tbody tr:hover { background: var(--surface-2); }
.kc-table td.kc-data { font-weight: 560; }
.kc-bank { font-weight: 580; }
.kc-bank-row { display: flex; align-items: center; gap: 0.55rem; }
.kc-dot {
  width: 8px; height: 8px; border-radius: 50%; flex: none;
  background: var(--brand);
}
.kc-camp { color: var(--ink); }
.kc-camp small { display: block; color: var(--ink-muted); font-size: 0.78rem; }
.kc-null { color: var(--ink-muted); }
.kc-row--best { background: var(--brand-tint); }
.kc-row--best:hover { background: var(--brand-tint); }
.kc-best-tag {
  display: inline-block; margin-left: 0.4rem;
  font-size: 0.66rem; font-weight: 700; letter-spacing: 0.03em;
  color: var(--brand-hover);
  border: 1px solid var(--brand);
  border-radius: 999px; padding: 0.05rem 0.4rem;
  vertical-align: middle;
}
.kc-src { color: var(--ink-muted); font-size: 0.82rem; cursor: help; }
.kc-src b { color: var(--brand-hover); font-weight: 600; }

/* ---- chips ---- */
.kc-chip {
  display: inline-block;
  background: var(--surface-2);
  color: var(--ink-muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.02em;
  padding: 0.12rem 0.55rem;
  white-space: nowrap;
}

/* ---- badges (always icon + text, color-blind safe) ---- */
.kc-badge {
  display: inline-flex; align-items: center; gap: 0.3rem;
  border-radius: 999px; padding: 0.18rem 0.6rem;
  font-size: 0.76rem; font-weight: 600;
  border: 1px solid transparent;
}
.kc-badge--preview { background: oklch(0.95 0.03 240); color: oklch(0.4 0.12 240);
  border-color: oklch(0.85 0.05 240); }
.kc-badge--stale { background: oklch(0.96 0.04 75); color: oklch(0.45 0.12 70);
  border-color: oklch(0.85 0.08 75); }
.kc-badge--ok { background: oklch(0.95 0.04 155); color: oklch(0.42 0.1 155);
  border-color: oklch(0.85 0.07 155); }

/* ---- teaching note / empty state ---- */
.kc-note {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-panel);
  padding: 1rem 1.15rem;
  margin: 0.6rem 0;
}
.kc-note h4 { margin: 0 0 0.35rem; font-size: 0.95rem; font-weight: 620; }
.kc-note p { margin: 0; color: var(--ink-muted); font-size: 0.88rem; }

/* ---- native widget polish ---- */
[data-baseweb="tab-list"] { gap: 0.25rem; border-bottom: 1px solid var(--border); }
[data-baseweb="tab"] { font-weight: 560; }
[data-baseweb="tab"][aria-selected="true"] { color: var(--brand-hover); }
[data-testid="stChatMessage"] {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-panel);
}

/* ---- chat sources block (ADR 0009 contract) ---- */
.kc-sources { margin-top: 0.6rem; border-top: 1px dashed var(--border); padding-top: 0.55rem; }
.kc-sources .kc-src-head {
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.05em;
  text-transform: uppercase; color: var(--ink-muted); margin-bottom: 0.4rem;
}
.kc-source-item {
  font-size: 0.85rem; padding: 0.45rem 0;
  border-bottom: 1px solid var(--border);
}
.kc-source-item:last-child { border-bottom: none; }
.kc-source-item b { font-weight: 600; }
.kc-source-item em { color: var(--ink-muted); font-style: normal; }

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
</style>
"""


def inject_theme() -> None:
    """Inject the design system. Call once, first thing in the app."""
    st.markdown(_CSS, unsafe_allow_html=True)


def html(markup: str) -> None:
    """Render a raw-HTML block. Strips per-line leading whitespace and drops
    blank lines first — otherwise Streamlit's Markdown treats indented HTML as
    a code block (and blank lines split the block), printing the tags as text.
    """
    cleaned = "\n".join(ln.strip() for ln in markup.splitlines() if ln.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def esc(text: object) -> str:
    """HTML-escape any value going into injected markup."""
    return _stdhtml.escape(str(text))


def chip(label: str) -> str:
    return f'<span class="kc-chip">{esc(label)}</span>'


def badge(kind: str, text: str, icon: str = "") -> str:
    """kind: preview | stale | ok. Icon + text (never color alone)."""
    lead = f"{esc(icon)} " if icon else ""
    return f'<span class="kc-badge kc-badge--{esc(kind)}">{lead}{esc(text)}</span>'
