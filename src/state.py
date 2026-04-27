from __future__ import annotations

from typing import Any, Dict, List, Literal, TypedDict


class GraphState(TypedDict, total=False):
    building_data: Dict[str, Any]
    compliance_status: Dict[str, Any]
    available_grants: List[Dict[str, Any]]
    proposed_solutions: List[Dict[str, Any]]
    simulation_report: Dict[str, Any]
    human_approval: Dict[str, Any]
    audit_report: Dict[str, Any]
    affordability_passed: bool
    replan_count: int
    max_replans: int
    missing_data_questions: List[str]
    citations: List[Dict[str, str]]
    next_step: Literal[
        "data_auditor",
        "incentive_hunter",
        "retrofit_architect",
        "equity_manager",
        "human_input",
        "done",
    ]
