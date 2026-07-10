"""The FastAPI app (ADR 0022): JSON contract + SSE + the built SPA.

Endpoints mirror what the Streamlit dashboard and control panel already do —
this file is wiring only; logic lives in data.py / runs.py / events.py.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from banking_analysis.api import data, runs
from banking_analysis.api.schemas import (
    CampaignList,
    ChatRequest,
    ChatResponse,
    PipelineStatus,
    RunInfo,
    RunRequest,
    RunStarted,
    Stats,
)

SPA_DIST = Path(__file__).resolve().parents[3] / "web" / "dist"

app = FastAPI(title="KıyasAI API", version="1.0")

# Dev convenience only: the Vite dev server (localhost:5173) talks to this
# API cross-origin. In production the SPA is served BY this app (same
# origin), so CORS never applies. Localhost-only — still fully offline.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    try:
        runs.ensure_tables()  # idempotent migration (ADR 0022)
    except Exception:
        pass  # DB down — data endpoints degrade to sample, pipeline 503s


# --- data -------------------------------------------------------------------

@app.get("/api/stats", response_model=Stats)
def stats() -> Stats:
    return data.get_stats()


@app.get("/api/campaigns", response_model=CampaignList)
def campaigns(type: str | None = None) -> CampaignList:
    return data.get_campaigns(type)


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return data.get_answer(req.question)


# --- pipeline (ADR 0021) ------------------------------------------------------

@app.get("/api/pipeline/status", response_model=PipelineStatus)
def pipeline_status() -> PipelineStatus:
    from banking_analysis.control_panel import ops

    s = ops.status()
    model_ok, model_detail = ops.model_status()
    return PipelineStatus(
        db_ok=bool(s), model_ok=model_ok, model_detail=model_detail, **s
    )


@app.post("/api/pipeline/run", response_model=RunStarted, status_code=202)
def pipeline_run(req: RunRequest) -> RunStarted:
    try:
        run_id = runs.MANAGER.start(req.step)
    except KeyError:
        raise HTTPException(422, f"unknown step: {req.step}")
    except runs.StepBusy:
        raise HTTPException(409, f"{req.step} is already running")
    except Exception as exc:
        raise HTTPException(503, f"cannot start run (database down?): {exc}")
    return RunStarted(run_id=run_id, step=req.step)


@app.get("/api/pipeline/runs", response_model=list[RunInfo])
def pipeline_runs(limit: int = 20) -> list[RunInfo]:
    try:
        return [RunInfo(**r) for r in runs.fetch_runs(limit)]
    except Exception:
        raise HTTPException(503, "database unreachable")


@app.get("/api/pipeline/runs/{run_id}/events")
async def pipeline_run_events(run_id: int) -> StreamingResponse:
    """SSE: replay stored events, then tail until the run finishes.

    The DB is the source of truth (runs.py stores every event as it happens);
    this endpoint polls it server-side and pushes over one long-lived HTTP
    response — the browser just sees instant events (ADR 0022: SSE).
    """

    async def gen():
        last_seq = 0
        while True:
            try:
                events = await asyncio.to_thread(runs.fetch_events, run_id, last_seq)
                done = await asyncio.to_thread(runs.run_finished, run_id)
            except Exception:
                yield "event: error\ndata: {\"detail\": \"database unreachable\"}\n\n"
                return
            for e in events:
                last_seq = e["seq"]
                body = json.dumps(
                    {"seq": e["seq"], "type": e["event_type"], **e["payload"]},
                    ensure_ascii=False, default=str,
                )
                yield f"data: {body}\n\n"
            if done and not events:
                yield "event: end\ndata: {}\n\n"
                return
            await asyncio.sleep(0.4)

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --- SPA (mounted last so /api keeps priority) -------------------------------

if SPA_DIST.is_dir():
    app.mount("/", StaticFiles(directory=SPA_DIST, html=True), name="spa")
