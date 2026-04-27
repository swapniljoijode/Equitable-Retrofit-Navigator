from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from src.graph import build_graph
from src.state import GraphState
from src.tools.energy_enrichment import enrich_with_proxy_estimates
from src.tools.nyc_pluto import fetch_pluto_record, normalize_pluto_record


def load_building_profile(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_building_from_pluto(bbl: str | None, bin_number: str | None) -> tuple[dict, list[str]]:
    app_token = os.getenv("NYC_OPEN_DATA_APP_TOKEN")
    try:
        record = fetch_pluto_record(bbl=bbl, bin_number=bin_number, app_token=app_token)
        normalized = normalize_pluto_record(record)
        enriched = enrich_with_proxy_estimates(normalized)
        return enriched, [
            "Using low-confidence proxy estimates for annual cost, energy, and CO2e. "
            "Please replace with actual utility/benchmarking data when available."
        ]
    except ValueError as exc:
        fallback = {
            "building_id": "pluto_lookup_failed",
            "name": "Unknown NYC Building",
            "borough": "Unknown",
            "address": "Unknown",
            "units": 0,
            "heating_system": "unknown",
            "estimated_annual_utility_cost_usd": None,
            "estimated_annual_co2e_tons": None,
        }
        return fallback, [str(exc)]


def run() -> GraphState:
    app = build_graph()
    initial_questions: list[str] = []
    args = parse_args()
    if args.source == "pluto":
        building_data, initial_questions = load_building_from_pluto(bbl=args.bbl, bin_number=args.bin)
    else:
        building_data = load_building_profile("data/building_profile.json")
    initial_state: GraphState = {
        "building_data": building_data,
        "compliance_status": {},
        "available_grants": [],
        "proposed_solutions": [],
        "simulation_report": {},
        "human_approval": {"status": "pending"},
        "replan_count": 0,
        "max_replans": 3,
        "missing_data_questions": initial_questions,
        "citations": [],
    }
    return app.invoke(initial_state)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Equitable Retrofit Navigator graph.")
    parser.add_argument(
        "--source",
        choices=["mock", "pluto"],
        default="mock",
        help="Choose building data source.",
    )
    parser.add_argument("--bbl", default=None, help="NYC borough-block-lot identifier.")
    parser.add_argument("--bin", default=None, help="NYC Building Identification Number.")
    return parser.parse_args()


if __name__ == "__main__":
    final_state = run()
    print(json.dumps(final_state, indent=2))
