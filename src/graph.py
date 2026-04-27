from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.agents import (
    compliance_scout_node,
    data_auditor_node,
    equity_manager_node,
    human_approval_node,
    incentive_hunter_node,
    retrofit_architect_node,
    simulation_node,
)
from src.state import GraphState


def route_after_incentive(state: GraphState) -> str:
    grants = state.get("available_grants", [])
    return "retrofit_architect_replan" if len(grants) == 0 else "retrofit_architect"


def route_after_retrofit(state: GraphState) -> str:
    return "simulation_node"


def route_after_compliance(state: GraphState) -> str:
    next_step = state.get("next_step", "data_auditor")
    if next_step == "human_input":
        return END
    return "data_auditor"


def route_after_auditor(state: GraphState) -> str:
    next_step = state.get("next_step", "incentive_hunter")
    if next_step == "human_input":
        return END
    return "incentive_hunter"


def route_after_equity(state: GraphState) -> str:
    next_step = state.get("next_step", "done")
    if next_step == "retrofit_architect":
        return "retrofit_architect"
    if next_step == "human_input":
        return END
    return END


def route_after_human_approval(state: GraphState) -> str:
    next_step = state.get("next_step", "human_input")
    if next_step == "incentive_hunter":
        return "incentive_hunter"
    if next_step == "retrofit_architect":
        return "retrofit_architect"
    return END


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("compliance_scout", compliance_scout_node)
    graph.add_node("data_auditor", data_auditor_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("incentive_hunter", incentive_hunter_node)
    graph.add_node("retrofit_architect", retrofit_architect_node)
    graph.add_node("simulation_node", simulation_node)
    graph.add_node("equity_manager", equity_manager_node)

    graph.set_entry_point("compliance_scout")
    graph.add_conditional_edges(
        "compliance_scout",
        route_after_compliance,
        {
            "data_auditor": "data_auditor",
            END: END,
        },
    )
    graph.add_conditional_edges(
        "data_auditor",
        route_after_auditor,
        {
            "incentive_hunter": "human_approval",
            END: END,
        },
    )
    graph.add_conditional_edges(
        "human_approval",
        route_after_human_approval,
        {
            "incentive_hunter": "incentive_hunter",
            "retrofit_architect": "retrofit_architect",
            END: END,
        },
    )

    graph.add_conditional_edges(
        "incentive_hunter",
        route_after_incentive,
        {
            "retrofit_architect": "retrofit_architect",
            "retrofit_architect_replan": "retrofit_architect",
        },
    )
    graph.add_conditional_edges(
        "retrofit_architect",
        route_after_retrofit,
        {
            "simulation_node": "simulation_node",
        },
    )
    graph.add_edge("simulation_node", "equity_manager")
    graph.add_conditional_edges(
        "equity_manager",
        route_after_equity,
        {
            "retrofit_architect": "retrofit_architect",
            END: END,
        },
    )

    return graph.compile()
