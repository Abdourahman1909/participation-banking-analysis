---
status: accepted
---

# React + Vite + TypeScript SPA for the new public frontend

## Context

ADR 0012 chose Streamlit for the competition dashboard *behind a clean
backend boundary*, explicitly so it could be replaced later without touching
the intelligence layers. That later is now: the user wants one professional,
unified public UI (comparison dashboard + chatbot + a polished
pipeline-activity view) — the Streamlit look is not the face they want to
show TEKNOFEST judges. Full brief: `docs/frontend-rebuild-brief.md`.

Constraints that bound the choice (all competition-scored):
- **Fully offline / on-prem** — no CDN, no external fonts, no browser calls
  to anything but our own API.
- **Permissive licenses only** (MIT/Apache/BSD).
- Turkish-first UI; evidence-quote and answer+sources transparency
  (ADR 0016/0009) must survive the redesign.
- Competition timeline — the stack must reach "professional" fast.

## Decision

**React + Vite + TypeScript SPA**, styled with **Tailwind CSS + shadcn/ui**
(Radix primitives), charts via **Recharts**, served as static files by the
new **FastAPI** backend (the HTTP API layer that wraps storage + agent).
Fonts self-hosted. All dependencies MIT/permissive.

Why this combination beat the alternatives:
- **Builds to pure static assets** — `vite build` output is plain
  HTML/JS/CSS that FastAPI (or any static server) serves locally. Node.js
  exists only at build time on the dev machine; the deployed system stays
  fully offline with no Node runtime.
- **shadcn/ui vendors the component source into our repo** — we own the
  code, nothing phones home, and it looks professional out of the box.
- **Largest ecosystem** — the safest option under deadline pressure, and
  the same React knowledge transfers to the planned mobile app
  (React Native is one of its candidate stacks).
- Rejected: **Next.js** (adds an SSR Node server to the on-prem deployment
  for zero benefit — no SEO/SSR need), **Svelte** (fine technically, but a
  smaller component ecosystem means more hand-built UI, which costs
  timeline), **Jinja2 templates** (no build step, but a professional live
  monitor + chat experience would be mostly hand-rolled JS anyway).

## Consequences

- A new top-level frontend project (Vite) enters the repo, plus a build
  step: `npm install` + `vite build` on the dev machine. The build output is
  what ships; deployment machines never need Node.
- The FastAPI layer (next decision, own ADR) becomes a real, versionable
  API contract — the same one the future mobile app consumes.
- The Streamlit public dashboard keeps running until the new UI reaches
  parity (brief's rule); the Streamlit control panel (ADR 0018) is
  unaffected.
- The KıyasAI brand tokens in `DESIGN.md` get ported to Tailwind/CSS
  variables; `DESIGN.md`'s Streamlit-specific component specs are treated
  as history and will be refreshed once the new layout lands.
