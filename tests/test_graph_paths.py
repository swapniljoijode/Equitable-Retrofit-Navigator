from __future__ import annotations

from src.graph import build_graph
from src.main import load_building_profile


def _base_state():
    return {
        "building_data": load_building_profile("data/building_profile.json"),
        "compliance_status": {},
        "available_grants": [],
        "proposed_solutions": [],
        "simulation_report": {},
        "replan_count": 0,
        "max_replans": 3,
        "missing_data_questions": [],
        "citations": [],
    }


def test_pending_approval_pauses_for_human_input():
    app = build_graph()
    state = _base_state()
    state["human_approval"] = {"status": "pending"}
    out = app.invoke(state)
    assert out["next_step"] == "human_input"
    assert out["available_grants"] == []
    assert out["proposed_solutions"] == []


def test_approved_path_reaches_done_with_simulation():
    app = build_graph()
    state = _base_state()
    state["human_approval"] = {"status": "approved"}
    out = app.invoke(state)
    assert out["next_step"] == "done"
    assert out["affordability_passed"] is True
    assert len(out["available_grants"]) >= 1
    assert len(out["proposed_solutions"]) >= 1
    assert bool(out["simulation_report"]) is True
