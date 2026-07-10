# Layer 6 + the API — "what people see, and the door in front of the data"

You know this layer best — this file is mostly the words to explain it.

## Two pieces, one product

**The API (FastAPI, Python)** — a "front door" running at port 8000. It
translates HTTP requests into calls to the layers: give me the campaigns,
answer this chat question, start a collection run, stream me the live run
activity. Frontends never touch the database or the model directly — they
knock on this one door. That boundary is why a future **mobile app** can
reuse the entire backend without changing anything.

**The web app (React + TypeScript)** — the KıyasAI interface itself,
compiled to plain static files that the same server hands out. Three views:

- **Panel** — the comparison table. Filter by product type, sort by rate,
  best offer highlighted. Every row opens to show the **verbatim evidence
  quote** and its validation badge — the product's soul made visible.
- **Sohbet** — the chatbot, with sources under every answer.
- **Monitör** — the pipeline, live: funnel counts, health badges, run
  buttons, and a clean timeline of what the robots are doing right now
  (this replaced watching raw terminal logs).

## Two technical ideas worth knowing

- **Live updates use SSE (Server-Sent Events):** the browser keeps one
  long HTTP connection open and the server pushes each event ("Kuveyt Türk
  10/10 collected") the moment it happens. Simpler than WebSocket because
  we only need one direction — server to browser. Events are also saved in
  the database, so refreshing the page never loses history.
- **Fully offline by construction:** the app is self-contained static
  files — system fonts, no CDN, no external calls. The browser talks only
  to our own server. You can unplug the internet and the interface works
  (only new extraction needs the model machine).

## If someone asks…

- *"Why did you build a separate API instead of one app?"* — "Clean
  boundary: today one web frontend, tomorrow a mobile app, same backend.
  It also let us replace our first Streamlit interface without touching
  any layer."
- *"Is the interface calling any cloud service?"* — "None. Static files
  and one local API. Offline is a competition requirement and a feature —
  nothing is phoning home."
- *"What's the tech?"* — "React + TypeScript + Tailwind for the interface,
  FastAPI in Python for the API, Server-Sent Events for the live monitor,
  all packaged in Docker."
