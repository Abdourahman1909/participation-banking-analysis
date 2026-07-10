# Running KıyasAI on Windows

A step-by-step guide for teammates on Windows. Follow **Option A** — it runs
everything in Docker on one machine, needs no Python and no config file, and
is the hardest to break. (See the main `README.md` for the split-machine
setup, Option B.)

> Do every command in **PowerShell** (search "PowerShell" in the Start menu),
> **not** the old `cmd`. Run them from inside the project folder.

---

## 1. Install the two tools you need

1. **Docker Desktop** — https://www.docker.com/products/docker-desktop/
   - During install, leave **"Use WSL 2 instead of Hyper-V"** checked.
   - Restart the computer if it asks.
   - Open Docker Desktop once and wait until it says **"Engine running"**
     (green, bottom-left). Leave it running whenever you use the project.
   - If it complains about virtualization, enable **Virtualization / SVM** in
     the BIOS, or turn on Windows features **"Virtual Machine Platform"** and
     **"Windows Subsystem for Linux"** (Start → "Turn Windows features on or off").

2. **Git for Windows** — https://git-scm.com/download/win
   (Accept all the defaults.)

That's everything. You do **not** need to install Python, Postgres, or Ollama
by hand — Docker brings them.

---

## 2. Get the code

In PowerShell (type the URL exactly — **no angle brackets**; PowerShell treats
`<` and `>` as special characters and will error):

```powershell
git clone https://github.com/Abdourahman1909/participation-banking-analysis.git
cd participation-banking-analysis
```

---

## 3. Choose your model setup

The language model (Qwen 2.5, ~5 GB) is the **only heavy part**. Everything
else is light. Pick the tier that matches your machine — the app works in all
three, only *new extraction* needs a reachable model.

### Tier 1 — Run the model on your own machine
For a machine with a **good GPU**, or at least **≥ 12 GB RAM** to tolerate CPU.

```powershell
docker compose up -d --build
docker compose exec ollama ollama pull qwen2.5:7b-instruct   # one-time, ~5 GB
```
> **No GPU (CPU only)?** Still works, just slower. Open `docker-compose.yml`,
> put a `#` in front of each line of the `deploy:` block under the `ollama:`
> service (the lines about `resources` / `devices` / `nvidia` / `gpu`), save,
> then run `docker compose up -d` again.

### Tier 2 — Use a teammate's machine for the model (recommended for weak laptops)
Your laptop runs the app; **one teammate with a strong PC** runs the model and
shares it over the same Wi-Fi. Nobody else downloads the 5 GB model.

- On the **strong machine** (any OS), that person installs Ollama
  (https://ollama.com/download), runs `ollama pull qwen2.5:7b-instruct`, then
  serves it to the network:
  - Windows PowerShell: `$env:OLLAMA_HOST="0.0.0.0"; ollama serve`
  - They find their local IP with `ipconfig` (e.g. `192.168.1.42`).
- On **your** machine, create a file named `.env` next to `docker-compose.yml`
  **using Notepad or VS Code** (not PowerShell `>`), containing one line:
  ```
  OLLAMA_URL=http://192.168.1.42:11434
  ```
  (use the strong machine's real IP). Then start everything **except** the local
  model service:
  ```powershell
  docker compose up -d --build postgres api app control-panel scheduler
  ```

### Tier 3 — No model at all (lightest — for old / low-RAM laptops)
Just want to open the dashboard, browse data, work on the UI or scrapers, or
demo the interface? Skip the model entirely:

```powershell
docker compose up -d --build postgres api app control-panel scheduler
```
Everything opens and runs. The dashboard shows sample/preview data, and the
control panel will say **"Model sunucusu: kapalı"** — that's expected. The
collect and validate steps still work; only the **extraction** step needs a
model, so it just logs that it's skipped. You can point at a model later
(Tier 2) any time with no reinstall.

---

## 4. Open it

- **KıyasAI (the main product)** → http://localhost:8000
  Three views in one app: **Panel** (comparison), **Sohbet** (chatbot) and
  **Monitör** — in Monitör, run the three steps in order,
  **Toplama** (collect) → **Çıkarım** (extract) → **Doğrulama** (validate),
  and watch them work live. Then check Panel for the compared campaigns.
- Old dashboard (Streamlit, being replaced) → http://localhost:8501
- Control panel (internal tools: SQL, table browser) → http://localhost:8502

You don't need to install Node.js for the new interface — Docker builds it
during `docker compose up --build`.

---

## 5. Everyday commands

```powershell
docker compose ps                 # see what's running
docker compose logs -f scheduler  # watch the pipeline (Ctrl+C to stop watching)
docker compose stop               # pause everything (data kept)
docker compose up -d              # start again
docker compose down               # stop and remove containers (data kept)
```

Your scraped/extracted data lives in a Docker volume and **survives** all of
the above.

---

## ⚠️ The one thing NOT to do

```powershell
docker compose down -v     # ❌ the -v ERASES the database (all scraped data)
```

Only use `-v` if you deliberately want a clean wipe. Without `-v`, your data is
always safe.

---

## Windows gotchas (read if something misbehaves)

- **Docker Desktop must be open and "running"** before any `docker` command.
  If you get *"error during connect / docker daemon is not running"*, just
  start Docker Desktop and wait for the green light.
- **Don't create the `.env` file with PowerShell `>`.** Commands like
  `echo "X=Y" > .env` in Windows PowerShell can save the file in an encoding
  the app can't read. You don't need `.env` at all for Option A. If you ever do
  (Option B), create it with **Notepad** or **VS Code** and save as **UTF-8**.
- **"Port already in use" (8000 / 8501 / 8502 / 5432)** — another program is
  using that port. Close it, or change the port on the left side of the mapping
  in `docker-compose.yml` (e.g. `"8601:8501"`).
- **Antivirus / firewall popup** the first time — allow Docker through; it only
  talks to your own machine (localhost), nothing external.
- **Editing project files:** use **VS Code** or **Notepad++**. Line endings do
  not break this project, but avoid pasting into apps that change quotes or
  encoding.

---

## Why this is safe

- Cloning the repo copies **only code** — never anyone's scraped data, which
  lives in a Docker volume on each machine separately.
- Everything runs **locally / offline** (a competition requirement): no API
  keys, no external servers, nothing leaves your computer.
- If a container ever gets into a bad state, `docker compose down` then
  `docker compose up -d --build` rebuilds it cleanly without touching your data.
