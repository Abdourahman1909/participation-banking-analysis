---
status: accepted
---

# Agent responses are structured {answer_text, sources[]}, not inline-cited prose

With evidence quotes (ADR 0004) and validation flags (ADR 0008) both
existing, the open question was how they reach the user. Inline-quoting
every claim in the chatbot's prose was rejected — it clutters answers and
hurts the spec's own "outputs should be accurate and understandable"
criterion. Instead, the agent's response is structured as a clean natural
-language `answer_text` plus a separate `sources[]` list (the evidence
quotes behind the claims), which the Streamlit UI renders as an expandable
"Show sources" section under each chat answer, and the dashboard renders as
an expandable per-cell source on comparison tables. This fixes the contract
between agent and frontend now, since changing response shape later would
require touching both the agent's output schema and the UI rendering code.
