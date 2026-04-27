from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from src.graph import build_graph


def load_mock_building() -> Dict[str, Any]:
    return json.loads(Path("data/building_profile.json").read_text(encoding="utf-8"))


def run_with_approval(approval_status: str, reason: str) -> Dict[str, Any]:
    graph = build_graph()
    initial_state = {
        "building_data": load_mock_building(),
        "compliance_status": {},
        "available_grants": [],
        "proposed_solutions": [],
        "simulation_report": {},
        "human_approval": {
            "status": approval_status,
            "reason": reason.strip(),
        },
        "replan_count": 0,
        "max_replans": 3,
        "missing_data_questions": [],
        "citations": [],
    }
    return graph.invoke(initial_state)


st.set_page_config(page_title="KC3 Human Approval", page_icon="🏢", layout="wide")
st.title("Equitable Retrofit Navigator - Human Approval")
st.caption("Consultant checkpoint before incentive workflow continues.")

approval_status = st.radio(
    "Consultant Decision",
    options=["pending", "approved", "rejected"],
    horizontal=True,
)
reason = st.text_area("Decision notes", placeholder="Optional rationale or constraints...")

if st.button("Run Workflow"):
    result = run_with_approval(approval_status=approval_status, reason=reason)
    st.subheader("Workflow Result")
    st.json(result)

    st.subheader("Key Status")
    st.write(f"Next Step: `{result.get('next_step', 'unknown')}`")
    st.write(f"Affordability Passed: `{result.get('affordability_passed', False)}`")
    questions = result.get("missing_data_questions", [])
    if questions:
        st.warning("Action Required")
        for q in questions:
            st.write(f"- {q}")
