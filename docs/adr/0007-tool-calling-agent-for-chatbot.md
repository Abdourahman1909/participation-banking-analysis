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

**Amendment (post-build): scope guard + grounded recommendations.** The agent
is a small, cheap model, so the same verify-don't-trust posture as extraction
(ADR 0016) applies:

- **Topical scope guard, not a straitjacket.** A system prompt confines it to
  Turkish participation-banking campaigns/products. *In scope:* clarifying
  questions (definitions, "tell me more"), comparisons, and **recommendations**
  — all encouraged, conversational, multi-turn. *Out of scope:* anything else
  ("write code", "tell a joke") → politely decline and redirect.
- **Recommendations are grounded, not advice.** The agent recommends *from the
  data it retrieved* ("X has the lowest rate — here's the source"), never
  open-ended financial advice from its own knowledge.
- **Sources are attached deterministically (ADR 0009).** Sources come from the
  actual tool results the agent used, not from the model claiming a citation —
  so an answer can't cite something it didn't retrieve.
- **Tiny blast radius by design.** Tools are read-only DB queries; the model
  is local/offline with no external calls and no sensitive data. Even a
  successful jailbreak can at worst produce off-topic text — it cannot leak,
  modify, or destroy anything. The scope guard is for professionalism; the
  read-only/offline/fixed-toolset design is what makes misuse harmless.
