"""HTTP API boundary (ADR 0022) — NOT a pipeline layer. The FastAPI face of
the clean backend boundary from ADR 0012: wraps storage (Layer 4), the agent
(Layer 5), and the layer runners (pipeline operations, ADR 0021) so the SPA
frontend — and later the mobile app — talk to one contract over HTTP. Serves
the built SPA as static files. Run it:

    uv run python -m banking_analysis.api.runner
"""
