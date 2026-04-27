from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from src.llm.openrouter import refine_node_output
from src.state import GraphState


def _merge_citations(new_items: List[Dict[str, str]], prior_items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    merged = []
    seen = set()
    for item in new_items + prior_items:
        key = (item.get("source_type", ""), item.get("reference", ""), item.get("url", ""))
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
    return merged


class ComplianceOutput(BaseModel):
    compliance_status: Dict[str, Any]
    citations: List[Dict[str, str]]
    missing_data_questions: List[str] = Field(default_factory=list)
    next_step: str


class AuditOutput(BaseModel):
    audit_report: Dict[str, Any]
    missing_data_questions: List[str] = Field(default_factory=list)
    next_step: str


class IncentiveOutput(BaseModel):
    available_grants: List[Dict[str, Any]]
    citations: List[Dict[str, str]]
    replan_count: int
    next_step: str


class RetrofitOutput(BaseModel):
    proposed_solutions: List[Dict[str, Any]]
    citations: List[Dict[str, str]]
    replan_count: int
    next_step: str


class SimulationOutput(BaseModel):
    simulation_report: Dict[str, Any]
    citations: List[Dict[str, str]]
    next_step: str


class EquityOutput(BaseModel):
    affordability_passed: bool
    audit_report: Dict[str, Any]
    missing_data_questions: List[str] = Field(default_factory=list)
    next_step: str


class HumanApprovalOutput(BaseModel):
    human_approval: Dict[str, Any]
    missing_data_questions: List[str] = Field(default_factory=list)
    next_step: str


def compliance_scout_node(state: GraphState) -> GraphState:
    building = state.get("building_data", {})
    prior_questions = list(state.get("missing_data_questions", []))
    prior_citations = list(state.get("citations", []))
    raw_co2e = building.get("estimated_annual_co2e_tons", 0)
    co2e_tons = float(raw_co2e or 0)
    fines_estimate = max((co2e_tons - 300) * 268, 0)

    missing = []
    for field in ("year_built", "estimated_annual_co2e_tons", "estimated_annual_energy_use_mmbtu"):
        if field not in building:
            missing.append(f"Please provide {field} for LL97 compliance modeling.")

    result = ComplianceOutput(
        compliance_status={
            "ll97_risk_level": "high" if fines_estimate > 0 else "low",
            "estimated_annual_fine_usd": round(fines_estimate, 2),
            "assumption_note": "Mock estimation only; replace with official emissions intensity calculations.",
        },
        citations=_merge_citations([
            {
                "source_type": "law",
                "reference": "NYC LL97 (Article 320) - annual emissions limits and penalties",
                "url": "https://www.nyc.gov/site/sustainablebuildings/ll97/local-law-97.page",
            }
        ], prior_citations),
        missing_data_questions=prior_questions + missing,
        next_step="data_auditor" if not missing else "human_input",
    )
    draft = result.model_dump()
    return refine_node_output("compliance_scout", state, draft)


def data_auditor_node(state: GraphState) -> GraphState:
    building = state.get("building_data", {})
    prior_questions = list(state.get("missing_data_questions", []))
    required = [
        "units",
        "heating_system",
        "estimated_annual_utility_cost_usd",
        "estimated_annual_co2e_tons",
    ]
    missing = [f"Missing required building field: {key}" for key in required if key not in building]
    if int(building.get("units", 0) or 0) <= 0:
        missing.append("Missing or invalid residential unit count. Please provide unit count.")
    if "unknown" in str(building.get("heating_system", "")).lower():
        missing.append("Heating system type is unknown. Please provide fuel and system type.")

    report = {
        "is_data_complete": len(missing) == 0,
        "quality_score": 1.0 if len(missing) == 0 else max(0.2, 1.0 - (0.2 * len(missing))),
    }
    result = AuditOutput(
        audit_report=report,
        missing_data_questions=prior_questions + missing,
        next_step="incentive_hunter" if len(missing) == 0 else "human_input",
    )
    draft = result.model_dump()
    return refine_node_output("data_auditor", state, draft)


def incentive_hunter_node(state: GraphState) -> GraphState:
    building = state.get("building_data", {})
    prior_citations = list(state.get("citations", []))
    oil_heat = "oil" in str(building.get("heating_system", "")).lower()

    grants: List[Dict[str, Any]] = []
    if oil_heat:
        grants.append(
            {
                "name": "NYSERDA Multifamily Performance Program (example)",
                "estimated_value_usd": 45000,
                "eligibility_note": "Mock eligibility for affordable multifamily energy upgrades.",
                "link": "https://www.nyserda.ny.gov/",
            }
        )

    no_grants = len(grants) == 0
    result = IncentiveOutput(
        available_grants=grants,
        citations=_merge_citations([
            {
                "source_type": "grant",
                "reference": "NYSERDA Programs Directory",
                "url": "https://www.nyserda.ny.gov/All-Programs",
            }
        ], prior_citations),
        replan_count=1 if no_grants else state.get("replan_count", 0),
        next_step="retrofit_architect_replan" if no_grants else "retrofit_architect",
    )
    draft = result.model_dump()
    return refine_node_output("incentive_hunter", state, draft)


def human_approval_node(state: GraphState) -> GraphState:
    approval = state.get("human_approval", {})
    prior_questions = list(state.get("missing_data_questions", []))

    status = approval.get("status", "pending")
    if status == "approved":
        draft = HumanApprovalOutput(
            human_approval=approval,
            missing_data_questions=prior_questions,
            next_step="incentive_hunter",
        ).model_dump()
        return refine_node_output("human_approval", state, draft)

    if status == "rejected":
        reason = approval.get("reason", "No reason provided.")
        draft = HumanApprovalOutput(
            human_approval=approval,
            missing_data_questions=prior_questions + [f"Plan rejected by consultant: {reason}"],
            next_step="retrofit_architect",
        ).model_dump()
        return refine_node_output("human_approval", state, draft)

    draft = HumanApprovalOutput(
        human_approval={
            "status": "pending",
            "requested_for": "grant_submission",
            "note": "Awaiting KC3 consultant approval before incentive workflow continues.",
        },
        missing_data_questions=prior_questions
        + [
            "Human approval required: open the Streamlit dashboard and approve or reject before grant workflow can continue."
        ],
        next_step="human_input",
    ).model_dump()
    return refine_node_output("human_approval", state, draft)


def retrofit_architect_node(state: GraphState) -> GraphState:
    building = state.get("building_data", {})
    grants = state.get("available_grants", [])
    replan_count = state.get("replan_count", 0)
    prior_citations = list(state.get("citations", []))

    base_cost = 220000
    grant_value = sum(float(item.get("estimated_value_usd", 0)) for item in grants)
    effective_cost = max(base_cost - grant_value, 70000)
    bill_reduction_pct = 0.11 if replan_count == 0 else 0.17
    co2e_reduction_pct = 0.19 if replan_count == 0 else 0.26

    solution = {
        "package_name": "Boiler electrification + envelope tune-up",
        "measures": [
            "Replace oil boiler with air-source heat pump system",
            "Seal envelope leaks and add attic insulation",
            "Install smart thermostatic controls",
        ],
        "estimated_capex_usd": round(effective_cost, 2),
        "estimated_bill_reduction_pct": round(bill_reduction_pct * 100, 1),
        "estimated_co2e_reduction_pct": round(co2e_reduction_pct * 100, 1),
        "comfort_impact": "positive",
        "assumption_note": "Mock engineering estimate for scaffolding only.",
    }

    result = RetrofitOutput(
        proposed_solutions=[solution],
        citations=_merge_citations([
            {
                "source_type": "technical",
                "reference": "ASHP retrofit best practices (placeholder)",
                "url": "https://www.energy.gov/",
            }
        ], prior_citations),
        replan_count=replan_count + 1,
        next_step="simulation_node",
    )
    draft = result.model_dump()
    return refine_node_output("retrofit_architect", state, draft)


def simulation_node(state: GraphState) -> GraphState:
    building = state.get("building_data", {})
    solutions = state.get("proposed_solutions", [])
    prior_citations = list(state.get("citations", []))

    base_mmbtu = float(building.get("estimated_annual_energy_use_mmbtu", 0) or 0)
    if base_mmbtu <= 0:
        base_mmbtu = 4200.0

    reduction_pct = 0.0
    if solutions:
        reduction_pct = float(solutions[0].get("estimated_co2e_reduction_pct", 0) or 0) / 100.0

    seasonal_weights = [0.12, 0.11, 0.1, 0.08, 0.07, 0.06, 0.05, 0.05, 0.06, 0.08, 0.1, 0.12]
    monthly_projection = []
    for idx, weight in enumerate(seasonal_weights, start=1):
        baseline = round(base_mmbtu * weight, 2)
        post = round(baseline * (1 - reduction_pct), 2)
        monthly_projection.append(
            {
                "month": idx,
                "baseline_mmbtu": baseline,
                "post_retrofit_mmbtu": post,
                "delta_mmbtu": round(baseline - post, 2),
            }
        )

    annual_baseline = round(sum(item["baseline_mmbtu"] for item in monthly_projection), 2)
    annual_post = round(sum(item["post_retrofit_mmbtu"] for item in monthly_projection), 2)

    result = SimulationOutput(
        simulation_report={
            "horizon_months": 12,
            "city_weather_profile": "NYC typical seasonal weighting proxy",
            "annual_baseline_mmbtu": annual_baseline,
            "annual_post_retrofit_mmbtu": annual_post,
            "annual_savings_mmbtu": round(annual_baseline - annual_post, 2),
            "monthly_projection": monthly_projection,
            "assumption_note": (
                "Proxy seasonal simulation for planning. Replace with NOAA/NYC weather history "
                "and calibrated building model for production use."
            ),
        },
        citations=_merge_citations([
            {
                "source_type": "weather",
                "reference": "NOAA climate normals (placeholder reference)",
                "url": "https://www.ncei.noaa.gov/",
            }
        ], prior_citations),
        next_step="equity_manager",
    )
    draft = result.model_dump()
    return refine_node_output("simulation_node", state, draft)


def equity_manager_node(state: GraphState) -> GraphState:
    solutions = state.get("proposed_solutions", [])
    prior_questions = list(state.get("missing_data_questions", []))
    max_replans = state.get("max_replans", 3)
    replan_count = state.get("replan_count", 0)
    bill_reduction = 0.0
    if solutions:
        bill_reduction = float(solutions[0].get("estimated_bill_reduction_pct", 0))
    passed = bill_reduction >= 15.0

    next_step = "done"
    questions: List[str] = []
    if not passed and replan_count < max_replans:
        next_step = "retrofit_architect"
    elif not passed and replan_count >= max_replans:
        next_step = "human_input"
        questions.append(
            "Unable to reach the 15% resident bill reduction target with current assumptions. "
            "Please provide constraints for rent burden limits, acceptable payback, and preferred measures."
        )

    result = EquityOutput(
        affordability_passed=passed,
        audit_report={
            "target_bill_reduction_pct": 15.0,
            "actual_bill_reduction_pct": bill_reduction,
            "comfort_priority": "maintain_or_improve",
            "affordability_status": "pass" if passed else "replan_required",
        },
        missing_data_questions=prior_questions + questions,
        next_step=next_step,
    )
    draft = result.model_dump()
    return refine_node_output("equity_manager", state, draft)
