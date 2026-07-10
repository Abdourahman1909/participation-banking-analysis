# Design

Visual system for the Participation Banking Analysis frontend (Layer 6,
Streamlit). Strategic brief lives in `PRODUCT.md`. Register: **product**
(design serves the task). Implemented via `.streamlit/config.toml` (base
theme) + injected CSS in `src/banking_analysis/frontend/theme.py`.

## Theme

Light. One sentence of scene: *a Turkish banking customer (or a competition
judge) comparing campaigns at a desk, in daylight, wanting to trust what they
see.* Daylight + trust + read-heavy data ⇒ light surface, high contrast,
quiet chrome. Color strategy: **Restrained** (product floor) — a near-pure
white surface, one teal-green brand color for actions/selection/state, and a
small set of semantic colors. The mood lives in the brand color and the
typography, not in a tinted background.

## Color

OKLCH throughout. Pure-white content surface; the teal-green carries the
brand (heritage nod to participation banking, deliberately *not* the generic
finance navy).

| Role | OKLCH | Use |
|---|---|---|
| `--bg` | `oklch(1 0 0)` | content background (pure white) |
| `--surface` | `oklch(0.985 0.004 178)` | panels, sidebar, table header — a whisper of teal |
| `--surface-2` | `oklch(0.965 0.006 178)` | row hover, chips |
| `--ink` | `oklch(0.21 0.018 195)` | primary text (≈13:1 on white) |
| `--ink-muted` | `oklch(0.46 0.016 200)` | secondary text (≥4.6:1 on white) |
| `--border` | `oklch(0.9 0.006 195)` | hairlines, table rules |
| `--border-strong` | `oklch(0.82 0.008 195)` | focus rings, active borders |
| `--brand` | `oklch(0.52 0.09 178)` | primary actions, selected state, links |
| `--brand-hover` | `oklch(0.46 0.092 178)` | hover/active of brand |
| `--brand-tint` | `oklch(0.95 0.03 178)` | selected-row wash, best-value highlight |
| `--success` | `oklch(0.55 0.11 155)` | valid field, positive |
| `--warning` | `oklch(0.72 0.13 75)` | stale data, caution |
| `--danger` | `oklch(0.55 0.18 25)` | invalid field, error |
| `--info` | `oklch(0.55 0.1 240)` | informational badges |

Hex mirror for `config.toml` (Streamlit wants hex): brand `#0F8A77`,
bg `#FFFFFF`, surface `#F3F6F5`, ink `#16201F`.

Rules: accent only for action/selection/state, never decoration. Semantic
colors always paired with an icon or text label (color-blind safe). Campaign
types render as **neutral** chips (tinted surface, not a rainbow per type) —
neutrality is a brand principle.

## Typography

One family, system stack (offline constraint — no font CDN at runtime):
`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Ubuntu, Cantarell,
"Helvetica Neue", Arial, sans-serif`. Numbers use `font-feature-settings:
"tnum" 1, "cv01" 1` (tabular figures) so rates/amounts align in columns.

Fixed rem scale (product UIs view at consistent DPI — no fluid clamp):

| Token | Size / weight / tracking | Use |
|---|---|---|
| display | 1.6rem / 650 / -0.02em | page title (brand mark) |
| h2 | 1.15rem / 620 / -0.01em | section headers |
| body | 0.94rem / 420 / 0 | default text |
| data | 0.94rem / 560 / 0, tnum | rates, amounts, terms in the table |
| label | 0.75rem / 600 / 0.02em, uppercase | column headers, chip text |
| caption | 0.8rem / 420 / 0 | secondary / muted notes |

Scale ratio ~1.2. No display fonts anywhere in UI/labels/data.

## Components

- **App header** — brand mark (teal diamond + "KıyasAI" wordmark) on
  the left, a one-line tagline, and the live stat strip on the right. Sits on
  `--surface` with a bottom hairline. Not a hero.
- **Stat strip** — modest inline counts (`10 banka · 13 kampanya · 8 ürün
  tipi · Son toplama: …`). Plain text rhythm, *not* big-number KPI cards.
- **Nav** — two views as tabs: **Panel** (dashboard) / **Sohbet** (chat).
- **Filter bar** — product-type selectbox + sort selectbox, on `--surface`,
  rounded 10px, hairline border. Native Streamlit widgets, themed.
- **Comparison table** — custom HTML for full control. Sticky header on
  `--surface`; rows separated by `--border` hairlines (no card-per-row, no
  zebra). Columns: Bank · Kampanya · Tür (chip) · Kâr payı · Vade · Tutar ·
  Kaynak. Best rate per current filter gets a `--brand-tint` wash + a "en
  düşük" tag (text, not color-only). Null value = "—" in `--ink-muted`.
  Row hover lifts to `--surface-2` (150ms). Evidence quote on the Kaynak cell
  (hover title + expander).
- **Chips** — campaign type, pill, `--surface-2` bg, `--ink-muted` text,
  uppercase label scale. Neutral by design.
- **Badges** — `preview` (sample data, `--info`), `stale` (`--warning` + ⏱),
  `valid`/`invalid` (`--success`/`--danger` + ✓/✕). Always icon + text.
- **Chat** — `st.chat_message` themed: user bubble `--brand-tint`, assistant
  on `--surface`. Assistant answers render the ADR-0009 contract: answer text
  followed by a **Kaynaklar** (sources) list, each linking bank + campaign +
  the evidence sentence. Marked as preview until the agent layer exists.
- **Empty / preview states** — when a layer hasn't run, an inline note that
  *teaches* (what's missing, why, what populates it), never a blank panel.

Radius scale: 8px (inputs/chips), 10px (panels), 12px (table container). No
24px+ over-rounding. Borders: single hairline OR a soft shadow, never both on
one element.

## Motion

Product-calm: 150–250ms, ease-out. State only — row hover, tab/selection
change, badge appearance. No page-load choreography. Every transition has a
`@media (prefers-reduced-motion: reduce)` no-op fallback.

## Layout

Centered content column, max-width ~1100px, comfortable padding. Streamlit's
default chrome (main menu, footer, toolbar) hidden for a product feel.
Responsive is structural: the table scrolls horizontally on narrow widths
rather than reflowing fluid type.
