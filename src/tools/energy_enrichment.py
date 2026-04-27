from __future__ import annotations

from typing import Any, Dict


def enrich_with_proxy_estimates(building_data: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(building_data)

    units = int(building_data.get("units", 0) or 0)
    heating_system = str(building_data.get("heating_system", "unknown")).lower()

    # Transparent proxy assumptions for early-stage planning only.
    baseline_cost_per_unit = 3800.0
    baseline_co2e_per_unit_tons = 6.2
    baseline_mmbtu_per_unit = 120.0

    if "oil" in heating_system:
        cost_multiplier = 1.15
        co2e_multiplier = 1.22
        mmbtu_multiplier = 1.08
    elif "gas" in heating_system:
        cost_multiplier = 1.0
        co2e_multiplier = 1.0
        mmbtu_multiplier = 1.0
    elif "electric" in heating_system:
        cost_multiplier = 0.95
        co2e_multiplier = 0.75
        mmbtu_multiplier = 0.88
    else:
        cost_multiplier = 1.05
        co2e_multiplier = 1.08
        mmbtu_multiplier = 1.02

    estimated_cost = round(units * baseline_cost_per_unit * cost_multiplier, 2)
    estimated_co2e = round(units * baseline_co2e_per_unit_tons * co2e_multiplier, 2)
    estimated_mmbtu = round(units * baseline_mmbtu_per_unit * mmbtu_multiplier, 2)

    if not enriched.get("estimated_annual_utility_cost_usd"):
        enriched["estimated_annual_utility_cost_usd"] = estimated_cost
    if not enriched.get("estimated_annual_co2e_tons"):
        enriched["estimated_annual_co2e_tons"] = estimated_co2e
    if not enriched.get("estimated_annual_energy_use_mmbtu"):
        enriched["estimated_annual_energy_use_mmbtu"] = estimated_mmbtu

    enriched["proxy_estimates"] = {
        "is_proxy": True,
        "model_name": "nyc_multifamily_proxy_v1",
        "confidence": "low",
        "assumptions": {
            "baseline_cost_per_unit_usd": baseline_cost_per_unit,
            "baseline_co2e_per_unit_tons": baseline_co2e_per_unit_tons,
            "baseline_mmbtu_per_unit": baseline_mmbtu_per_unit,
            "heating_adjustment_applied": heating_system or "unknown",
        },
        "disclaimer": (
            "Proxy estimates are planning placeholders and must be replaced with "
            "utility bills, benchmarking records, or engineered calculations."
        ),
    }

    return enriched
