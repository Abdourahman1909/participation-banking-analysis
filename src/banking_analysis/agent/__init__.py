"""Layer 5 — Reasoning (Agent). See docs/adr/0007, 0009.

Tool-calling agent over a fixed read-only toolset (tools.py) with a topical
scope guard and deterministic answer+sources. Code complete, offline-tested
with a fake model; needs the GPU model server (ADR 0015) to run for real.
Wired into the dashboard chat, which falls back to the canned preview until
campaigns exist and the model is reachable.
"""
