# Product

## Register

product

## Users

Three audiences, in priority order for the build:

1. **TEKNOFEST evaluators (primary, near-term).** Judges assessing the
   system during the 2026 competition. They sit down for a few minutes and
   need to grasp what the system does, trust that the numbers are real, and
   see the collect→extract→compare→answer pipeline working. Clarity and
   evident correctness beat feature breadth.
2. **A person comparing participation-banking products (the simulated end
   user).** Someone asking "which participation bank has the best housing
   finance / vehicle / card campaign right now, and on what terms?" They are
   not finance experts; they want a side-by-side answer they can trust, in
   Turkish, with the source.
3. **An analyst (later, startup path).** Wants density, export, history. Not
   the focus now, but nothing in the design should block it.

Context of use: Turkish-language financial campaign data, on-prem/offline,
read-only browsing plus a natural-language chatbot.

## Product Purpose

Make participation-banking products **comparable across banks**. The system
collects campaign text from the 10 BDDK participation banks, extracts
structured financial fields with a local LLM (each value carrying the source
sentence that proves it), and presents the result two ways: a **comparison
dashboard** (filter by product type, sort by rate/term) and a **chatbot**
that answers in natural language with citations. Success = a user (or judge)
can answer a cross-bank product question at a glance, and every number traces
back to the bank's own words.

## Brand Personality

Trustworthy, clear, neutral. The voice of a careful analyst, not a
salesperson. Three words: **trustworthy, clear, neutral**. It should feel
calm and self-contained (it runs offline; nothing is phoning home), and it
should feel like it belongs to no single bank — it sits *above* them.

## Anti-references

- **Default Streamlit.** The unstyled look (cramped, generic, the rainbow
  hamburger menu) is exactly what we are theming away from (ADR 0012).
- **Any single bank's branding.** This is a neutral aggregator. It must not
  borrow Kuveyt Türk's or Albaraka's colors/logo — that would imply
  endorsement and break neutrality.
- **Generic SaaS-cream + hero-metric template.** No giant gradient numbers,
  no "Trusted by 10,000 teams" energy. This is a tool, not a landing page.
- **Finance-terminal overload.** We deliberately chose calm/light over a
  dense dark Bloomberg clone; density serves the data, it isn't the aesthetic.

## Design Principles

1. **Neutral aggregator.** Own identity, equal footing for every bank. Never
   visually favor or mimic one. (Ties to ADR 0001's fixed, complete scope.)
2. **Evidence over assertion.** Every extracted number is shown *with* — or
   one click from — the source sentence that proves it. The UI makes
   provenance visible, never asks for blind trust. (ADR 0004, 0009.)
3. **Comparability is the product.** The cross-bank comparison is the hero
   surface; everything else supports it. Sorting and filtering by product
   type are first-class, not buried.
4. **Honest about gaps.** A missing value is shown as a plain "—", a
   non-campaign as "no campaign", and stale/sample data is labelled as such.
   We never fabricate completeness. (ADR 0014's null + no-campaign outcomes,
   CONTEXT.md's Stale Bank Data.)
5. **Offline calm.** No external calls, no spinners waiting on a network.
   The interface should feel instant and self-contained.

## Accessibility & Inclusion

- **Turkish-first UI.** User-facing labels in Turkish (the audience and data
  are Turkish); Turkish characters (ş ı ğ ü ö ç) must render correctly.
- **WCAG AA contrast.** Body text ≥ 4.5:1, large text ≥ 3:1. No light-gray
  body text on tinted white — a known Streamlit-default weakness.
- **Color is never the only signal.** Valid/invalid, stale, and best-rate
  states use an icon or text label in addition to color (color-blind safe).
- **Reduced motion respected.** All transitions have a
  `prefers-reduced-motion` fallback.
