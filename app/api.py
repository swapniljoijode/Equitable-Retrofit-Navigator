from __future__ import annotations

import os
import secrets
import uuid
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field

from src.audit import emit_audit_event, summarize_citations
from src.graph import build_graph
from src.main import load_building_profile, load_building_from_pluto

load_dotenv()


app = FastAPI(title="Equitable Retrofit Navigator API", version="0.1.0")


class RunRequest(BaseModel):
    source: str = Field(default="mock", pattern="^(mock|pluto)$")
    bbl: Optional[str] = None
    bin: Optional[str] = None
    human_approval_status: str = Field(default="pending", pattern="^(pending|approved|rejected)$")
    human_approval_reason: str = ""


def _initial_state(building_data: Dict[str, Any], initial_questions: list[str], approval_status: str, approval_reason: str):
    return {
        "building_data": building_data,
        "compliance_status": {},
        "available_grants": [],
        "proposed_solutions": [],
        "simulation_report": {},
        "human_approval": {"status": approval_status, "reason": approval_reason},
        "replan_count": 0,
        "max_replans": 3,
        "missing_data_questions": initial_questions,
        "citations": [],
    }


def _validate_api_key(x_api_key: Optional[str]) -> None:
    expected = os.getenv("API_AUTH_KEY")
    if not expected:
        raise HTTPException(status_code=500, detail="API_AUTH_KEY is not configured.")
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API key.")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/run")
def run_workflow(
    payload: RunRequest,
    response: Response,
    x_api_key: Optional[str] = Header(default=None),
    x_request_id: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _validate_api_key(x_api_key)
    request_id = x_request_id or str(uuid.uuid4())
    response.headers["X-Request-ID"] = request_id
    emit_audit_event(
        "workflow_run_requested",
        {
            "request_id": request_id,
            "source": payload.source,
            "human_approval_status": payload.human_approval_status,
            "has_bbl": bool(payload.bbl),
            "has_bin": bool(payload.bin),
        },
    )
    graph = build_graph()
    if payload.source == "pluto":
        building_data, initial_questions = load_building_from_pluto(bbl=payload.bbl, bin_number=payload.bin)
    else:
        building_data = load_building_profile("data/building_profile.json")
        initial_questions = []

    if payload.source == "pluto" and not payload.bbl and not payload.bin:
        raise HTTPException(status_code=400, detail="For source='pluto', provide bbl or bin.")

    state = _initial_state(
        building_data=building_data,
        initial_questions=initial_questions,
        approval_status=payload.human_approval_status,
        approval_reason=payload.human_approval_reason,
    )
    result = graph.invoke(state)
    emit_audit_event(
        "workflow_run_completed",
        {
            "request_id": request_id,
            "next_step": result.get("next_step"),
            "affordability_passed": result.get("affordability_passed"),
            "grants_count": len(result.get("available_grants", [])),
            "solutions_count": len(result.get("proposed_solutions", [])),
            "citations": summarize_citations(result.get("citations", [])),
            "human_approval": result.get("human_approval", {}),
        },
    )
    return result
