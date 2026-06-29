---
status: accepted
---

# Chatbot is a small tool-calling agent, not a hand-coded intent-parsing pipeline

Considered a fixed pipeline (our own code parses the question for bank
names/product type, runs a deterministic SQL query, hands the result to the
LLM only for answer composition) versus letting the LLM choose tools and
arguments itself. We're going with a lightweight tool-calling agent with a
small, fixed toolset (e.g. `get_campaigns(bank?, product_type?)`,
`compare_banks(banks, criteria)`) and no hand-written intent parsing. This
is the "AI Language Agents Competition" — judges are scoring whether this is
an agent, not a chat-shaped function call — and Qwen2.5's function-calling
already generalizes across question phrasings better than hand-coded intent
parsing would. Toolset stays deliberately small: no vector tool (ADR 0006),
no live-scrape tool (ADR 0003).
