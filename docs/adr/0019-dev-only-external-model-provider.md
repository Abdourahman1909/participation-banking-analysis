---
status: accepted
---

# A dev-only external model provider, never in the competition submission

## Context

All six layers are code-complete, but the two model-dependent layers —
extraction (Layer 2) and the chatbot agent (Layer 5) — cannot produce real
output until a local model is running. Per ADR 0015 that model lives on a
teammate's GPU machine, which is still being set up. Meanwhile we want to test
that the extraction/agent plumbing actually works end to end against a real
model, not just the offline fakes.

The hard constraint: the competition requires the system to run **fully
on-prem / offline, with no external LLM APIs** (spec §5.9, ADR 0009). This is
scored. An external API in the submitted or demoed system would violate it.

## Decision

Add a second `ChatModel` implementation, `OpenAICompatClient`, that talks to
any OpenAI-compatible `/chat/completions` endpoint (Groq, OpenRouter, …), and a
`get_model()` factory that selects the provider from the `MODEL_PROVIDER`
environment variable. This is **development/testing only**, guarded so it can
never become the default:

- **Default is always local.** Unset / `ollama` / `local` → `OllamaClient`
  (the ADR 0015 on-prem model). Only an explicit `MODEL_PROVIDER=groq` (etc.)
  selects the external client.
- **It announces itself.** `get_model()` prints a loud stderr warning whenever
  the external provider is active, stating it is dev-only and invalid for the
  submission.
- **It needs an explicit key.** `OpenAICompatClient` raises if `MODEL_API_KEY`
  is unset — you cannot enable it by accident.
- **Shipped config stays local.** `.env.example` and `docker-compose.yml`
  default to `ollama`; the external block in `.env.example` is commented,
  documented as dev-only, and must never be committed as the active setting.

Groq is the documented default external base because it is free, fast, and
hosts the same **Qwen 2.5** family we run locally — so dev results are
comparable to the eventual on-prem behavior.

The seam is the existing `ChatModel` Protocol (ADR 0016), so this is additive:
no layer logic changes, extraction and the agent consume both clients
identically. `OpenAICompatClient.chat()` normalizes the OpenAI response to the
same message dict shape `OllamaClient` returns; `complete()` (the extraction
path) is the primary, fully-supported use. Agent tool-calling across strict
OpenAI endpoints is best-effort.

## Consequences

- We can measure extraction quality and exercise the chatbot now, before the
  GPU machine is ready, without touching the six layers.
- The offline constraint is preserved by construction: local is the default,
  external is opt-in, loud, and key-gated.
- **Release checklist:** before the competition submission/demo, confirm
  `MODEL_PROVIDER` is unset or `ollama` everywhere (env, `.env`, compose) so no
  external call can happen. This ADR is the reminder.
- Same "don't pick a tool you'll replace later" spirit as ADR 0002/0006: the
  provider seam also leaves room to swap local model backends later without
  touching callers.
