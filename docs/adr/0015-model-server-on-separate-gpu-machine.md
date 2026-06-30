---
status: accepted
---

# Model server runs on a separate GPU machine, reached over the LAN

Extraction (ADR 0004/0005) and the agent (ADR 0007) need a local Qwen2.5
model served by Ollama. The primary development machine has no usable GPU
(Intel integrated graphics, 7.6 GB RAM) — too little to run even a 7B model
acceptably. A teammate has a laptop with a real GPU.

We're running **Ollama + the model on the teammate's GPU laptop as a
network-reachable model server**, while the rest of the system (collection,
storage, validation, frontend) runs on the primary machine and reaches the
model over HTTP on the local network. The model's location is a config
value, not a code fact: extraction/agent code reads `OLLAMA_URL` from the
environment (default `http://localhost:11434`), so pointing at the GPU
machine is a one-line change (`OLLAMA_URL=http://<gpu-laptop>:11434`) and
nothing in the code is hardcoded to a single host.

This does **not** break the on-prem/offline constraint (CLAUDE.md): both
machines are the team's own hardware on the same local network — no external
API, no paid service, no data leaving the organization. A LAN call between
two owned laptops is not an external dependency.

Relationship to ADR 0013: the single `docker-compose` stack remains the
"ship it on one machine" topology, with `ollama` as a compose service. This
ADR covers the development/competition reality where the model lives on
different hardware than everything else. The two coexist — same code, the
only difference is what `OLLAMA_URL` points at.

Trade-off accepted: extraction and the agent depend on the GPU machine being
powered on and reachable on the network; if it's down, those two layers
can't run. Collection, storage, and the dashboard still work without it (the
dashboard already degrades to sample data), so a missing model server
degrades the system rather than breaking it — acceptable for the build phase.
The one number still needed to finalize the model size (7B vs 14B) is the
GPU's VRAM (`nvidia-smi`), per ADR 0005.
