# KıyasAI — Participation Banking Product Analysis

Compares financial products across Turkey's participation banks. It:

1. **Collects** campaign texts from the banks' websites,
2. **Extracts** structured fields (profit-share rate, term, amount) using a
   **local** language model,
3. **Validates** them with deterministic rules, and
4. serves the results as a **comparison dashboard** and a **chatbot**.

Everything runs on your own machines — no external/cloud services, no API keys.

---

## What you need

- **Docker** — [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  on macOS/Windows, or Docker Engine on Linux. That's the only hard requirement.
- **For the language model**, one of:
  - a machine with a decent **GPU** (best), or
  - any machine — it can run on **CPU** too, just slower.
- **~10 GB free disk** (Docker images + the model).

The model is **Qwen 2.5** served by [Ollama](https://ollama.com). Sizes:
| Model | Download | Good for |
|---|---|---|
| `qwen2.5:7b-instruct` (default) | ~5 GB | 8 GB RAM / 6 GB VRAM |
| `qwen2.5:14b-instruct` | ~9 GB | 12 GB+ VRAM, better accuracy |

---

## Option A — Everything on one machine (simplest)

Run the whole thing, model included, on a single computer.

```bash
# 1. Get the code
git clone <this-repo-url>
cd participation-banking-analysis

# 2. Start everything
docker compose up -d --build

# 3. Download the model once (into the running Ollama)
docker compose exec ollama ollama pull qwen2.5:7b-instruct
```

> No GPU? Open `docker-compose.yml` and comment out the `deploy:` block under
> the `ollama` service — it will run on CPU (slower, but works).

Now open:
- **Dashboard** → http://localhost:8501
- **Control panel** → http://localhost:8502

Skip to [Using it](#using-it).

---

## Option B — Model on a separate machine

Run the app on your laptop, but let a **second machine with a GPU** run the
model (both must be on the **same network**, e.g. same Wi-Fi).

### On the GPU machine
```bash
# 1. Install Ollama:  https://ollama.com/download
# 2. Download the model
ollama pull qwen2.5:7b-instruct
# 3. Serve it so other machines can reach it (not just localhost)
OLLAMA_HOST=0.0.0.0 ollama serve
```
Find this machine's local IP address (e.g. `192.168.1.42`):
- Linux/macOS: `hostname -I` or `ipconfig getifaddr en0`
- Windows: `ipconfig`

### On your laptop (the app)
```bash
git clone <this-repo-url>
cd participation-banking-analysis

# Tell the app where the model lives (use the GPU machine's IP)
echo "OLLAMA_URL=http://192.168.1.42:11434" > .env

# Start everything EXCEPT the local model service
docker compose up -d --build postgres app control-panel scheduler
```
Open http://localhost:8501 (dashboard) and http://localhost:8502 (control panel).

---

## Using it

**Control panel** (http://localhost:8502) is where you operate the system:

- **Çalıştır (Run)** — buttons to run each step:
  1. **Toplama** — scrape the banks
  2. **Çıkarım** — extract fields with the model
  3. **Doğrulama** — validate them
- **Durum (Status)** — pipeline progress, model-server status, counts
- **Veri (Data)** — browse the database tables
- **SQL** — run read-only queries

Run **Toplama → Çıkarım → Doğrulama** once, then open the **dashboard**
(http://localhost:8501) to compare campaigns and chat.

The system also runs this pipeline automatically on a schedule (daily by
default; change `PIPELINE_INTERVAL_SECONDS` in `docker-compose.yml`).

---

## Common commands

```bash
docker compose ps               # what's running
docker compose logs -f scheduler # watch the pipeline
docker compose down             # stop everything (data is kept)
docker compose down -v          # stop AND erase all data (fresh start)
```

Your data lives in a Docker volume (`pgdata`) and **survives restarts**. It is
kept separate from the code — cloning the repo does not copy scraped data.

---

## Configuration (optional)

Set these in a `.env` file next to `docker-compose.yml`:

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_URL` | `http://ollama:11434` | Where the model server is (use Option B's IP) |
| `OLLAMA_MODEL` | `qwen2.5:7b-instruct` | Which model to use (also `ollama pull` it) |
| `PIPELINE_INTERVAL_SECONDS` | `86400` | How often the pipeline auto-runs |

---

## Troubleshooting

- **Control panel says "Model sunucusu: kapalı"** — the model isn't reachable.
  Option A: did you run the `ollama pull` step? Option B: is the GPU machine
  serving with `OLLAMA_HOST=0.0.0.0`, on the same network, and is `OLLAMA_URL`
  set to its IP?
- **Port already in use (8501/8502/5432)** — something else is using it; stop
  that program or change the port mapping in `docker-compose.yml`.
- **"permission denied" on Docker (Linux)** — add yourself to the docker group:
  `sudo usermod -aG docker $USER`, then log out and back in.
- **Extraction is slow** — you're on CPU. It works, but a GPU (Option B) is
  much faster.

---

## For developers (without Docker)

You need Python 3.10+, [uv](https://docs.astral.sh/uv/), and a Postgres
database. Then:

```bash
uv sync
# point DATABASE_URL / OLLAMA_URL at your Postgres and Ollama, then:
uv run python -m banking_analysis.collection.runner    # collect
uv run python -m banking_analysis.extraction.runner    # extract
uv run python -m banking_analysis.validation.runner    # validate
uv run streamlit run src/banking_analysis/frontend/dashboard.py         # dashboard
uv run streamlit run src/banking_analysis/control_panel/app.py --server.port 8502  # control panel
uv run python tests/test_extraction.py   # tests (also test_validation.py, test_agent.py)
```
