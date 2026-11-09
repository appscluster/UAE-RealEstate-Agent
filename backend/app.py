from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import BackgroundTasks, Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from agent import corpus, llm, runner

app = FastAPI(title="Readiness")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TENANT_ID = os.environ.get("DEMO_TENANT", "tenant_sandstone")
RUN_HISTORY: Dict[str, list] = {}
RUN_SEQ: Dict[str, int] = {}
RUN_RESULTS: Dict[str, Dict[str, Any]] = {}
RUN_QUEUES: Dict[str, asyncio.Queue] = {}
DECISIONS: Dict[str, Dict[str, Any]] = {}
HISTORY_LOCK = threading.Lock()


def _db() -> sqlite3.Connection:
    from pathlib import Path
    path = Path("backend/var/readiness.db")
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
          decision_id TEXT PRIMARY KEY,
          report_id TEXT,
          run_id TEXT,
          tenant_id TEXT,
          deal_id TEXT,
          decision TEXT,
          actor TEXT,
          sent INTEGER,
          ts TEXT
        )
        """
    )
    return con


@app.get("/health")
async def health():
    return {"ok": True, "tenant_id": TENANT_ID}


@app.get("/api/session")
async def session():
    return {"tenant_id": TENANT_ID, "brokerage": "Sandstone Realty", "actor": "coordinator:demo"}


@app.get("/api/deals")
async def list_deals():
    deals = []
    for deal in corpus.load_deals().values():
        if deal["tenant_id"] != TENANT_ID:
            continue
        deals.append({
            "deal_id": deal["deal_id"],
            "project": deal["project"],
            "unit_id": deal["unit_id"],
            "developer": deal["developer"],
            "jurisdiction": deal["jurisdiction"],
            "asking_price_aed": deal["asking_price_aed"],
            "buyer_question": deal["buyer_question"],
        })
    return {"deals": deals}


@app.get("/api/deals/{deal_id}")
async def get_deal(deal_id: str):
    deal = corpus.get_deal(deal_id)
    if deal is None or deal["tenant_id"] != TENANT_ID:
        raise HTTPException(404, "deal not found")
    return {"deal": deal}


@app.get("/api/models")
async def models():
    return llm.list_models()


@app.post("/api/runs")
async def start_run(tasks: BackgroundTasks, payload: Dict[str, Any] = Body(...)):
    deal_id = str(payload.get("deal_id") or "")
    if not deal_id:
        raise HTTPException(400, "deal_id required")
    run_id = str(uuid.uuid4())
    RUN_HISTORY[run_id] = []
    RUN_SEQ[run_id] = 0

    def record(event: Dict[str, Any]) -> None:
        with HISTORY_LOCK:
            RUN_SEQ[run_id] += 1
            RUN_HISTORY[run_id].append({**event, "seq": RUN_SEQ[run_id]})

    async def work() -> None:
        try:
            state = await asyncio.to_thread(
                runner.run_deal,
                TENANT_ID,
                deal_id,
                record,
                payload.get("requested_tenant"),
                payload.get("question"),
                payload.get("model"),
            )
        except Exception as exc:
            record({"phase": "planner", "refused": "run_failed", "line": f"The run stopped. {exc}"})
            state = {"refused": True, "refusal_reason": "run_failed", "findings": [], "deal_id": deal_id}
        RUN_RESULTS[run_id] = state

    tasks.add_task(work)
    return {"run_id": run_id, "refused": False}


@app.get("/runs/{run_id}/history")
async def history(run_id: str):
    if run_id not in RUN_HISTORY:
        raise HTTPException(404, "run not found")
    return {"history": RUN_HISTORY[run_id], "seq": RUN_SEQ.get(run_id, 0)}


@app.get("/runs/{run_id}/events")
async def events(run_id: str):
    if run_id not in RUN_HISTORY:
        raise HTTPException(404, "run not found")

    async def generate():
        seen = 0
        while True:
            with HISTORY_LOCK:
                batch = list(RUN_HISTORY[run_id][seen:])
                total = len(RUN_HISTORY[run_id])
                finished = run_id in RUN_RESULTS
            for event in batch:
                seen += 1
                yield {"data": json.dumps(event)}
            if finished and seen >= total:
                yield {"data": json.dumps({"event": "done"})}
                break
            await asyncio.sleep(0.05)

    return EventSourceResponse(generate())


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    state = RUN_RESULTS.get(run_id)
    if state is None:
        raise HTTPException(404, "run not found")
    return {"run": state}


@app.post("/api/runs/{run_id}/decisions")
async def decide(run_id: str, payload: Dict[str, Any] = Body(...)):
    state = RUN_RESULTS.get(run_id)
    if state is None:
        raise HTTPException(404, "run not found")
    if state.get("refused") or not state.get("draft"):
        raise HTTPException(409, "nothing to approve")
    decision = str(payload.get("decision") or "")
    actor = str(payload.get("actor") or "")
    notes = {
        "approve": "The report is accepted for this file. Nothing is sent to a buyer.",
        "reject": "The report is back with the coordinator. Nothing is sent to a buyer.",
        "escalate": "The case is with the pod lead. Nothing is sent to a buyer.",
    }
    if decision not in notes:
        raise HTTPException(400, "decision must be approve, reject, or escalate")
    if not actor:
        raise HTTPException(400, "actor required")
    report_id = str(uuid.uuid4())
    decision_id = str(uuid.uuid4())
    record = {
        "decision_id": decision_id,
        "report_id": report_id,
        "run_id": run_id,
        "tenant_id": TENANT_ID,
        "deal_id": state["deal_id"],
        "decision": decision,
        "actor": actor,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    report = {**state["draft"], "deal_id": state["deal_id"], "run_id": run_id, "decision": decision}
    DECISIONS[report_id] = report
    state["decision"] = decision
    state["decision_note"] = notes[decision]
    con = _db()
    con.execute(
        "INSERT INTO decisions (decision_id, report_id, run_id, tenant_id, deal_id, decision, actor, sent, ts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (decision_id, report_id, run_id, TENANT_ID, state["deal_id"], decision, actor, 0, record["ts"]),
    )
    con.commit()
    con.close()
    return {"record": record, "delivery": {"sent": False, "note": notes[decision]}}


@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    report = DECISIONS.get(report_id)
    if report is None:
        raise HTTPException(404, "report not found")
    return {"report": report}
