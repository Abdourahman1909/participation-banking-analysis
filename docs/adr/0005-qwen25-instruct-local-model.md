---
status: accepted
---

# Qwen2.5-Instruct (7B or 14B, size TBD by hardware) as the local model

The spec requires the model to run fully on-prem with no data leaving the
organization (§5.9), and to be open-source with no licensing risk (§5.10).
Hardware is a teammate's laptop GPU (exact VRAM to be confirmed). We're
using Qwen2.5-Instruct, served locally via Ollama or vLLM, for both the
extraction engine and chatbot reasoning: it's Apache-2.0 licensed, has
noticeably stronger Turkish than same-size Llama/Mistral alternatives, and
has reliable schema-constrained JSON output, which the evidence-quote
extraction format (ADR 0004) depends on. Exact size (7B vs 14B) is decided
by the confirmed VRAM budget once known — 14B if it fits comfortably, 7B
otherwise.
