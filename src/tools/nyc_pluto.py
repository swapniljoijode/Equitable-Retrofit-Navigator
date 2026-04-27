from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


PLUTO_DATASET = "64uk-42ks"
PLUTO_API_ROOT = f"https://data.cityofnewyork.us/resource/{PLUTO_DATASET}.json"


def _build_query(bbl: Optional[str], bin_number: Optional[str], limit: int = 1) -> str:
    params = {"$limit": str(limit)}
    if bbl:
        params["bbl"] = bbl
    if bin_number:
        params["bin"] = bin_number
    return f"{PLUTO_API_ROOT}?{urllib.parse.urlencode(params)}"


def fetch_pluto_record(
    bbl: Optional[str] = None,
    bin_number: Optional[str] = None,
    app_token: Optional[str] = None,
) -> Dict[str, Any]:
    if not bbl and not bin_number:
        raise ValueError("Provide at least one identifier: bbl or bin_number.")

    url = _build_query(bbl=bbl, bin_number=bin_number)
    request = urllib.request.Request(url)
    if app_token:
        request.add_header("X-App-Token", app_token)

    with urllib.request.urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")

    rows: List[Dict[str, Any]] = json.loads(payload)
    if not rows:
        raise ValueError("No PLUTO records found for the provided identifier.")
    return rows[0]


def normalize_pluto_record(record: Dict[str, Any]) -> Dict[str, Any]:
    units = int(float(record.get("unitsres", 0) or 0))
    borough = str(record.get("borough", "Unknown"))
    address = " ".join(
        part
        for part in [
            str(record.get("address", "")).strip(),
            str(record.get("zip", "")).strip(),
        ]
        if part
    ).strip()
    year_built = _safe_int(record.get("yearbuilt"))

    return {
        "building_id": record.get("bbl") or record.get("bin") or "pluto_unknown",
        "name": f"NYC PLUTO Building {record.get('bbl', '')}".strip(),
        "borough": borough,
        "address": address or "Address unavailable from PLUTO record",
        "units": units,
        "year_built": year_built,
        "occupancy_type": record.get("bldgclass", "unknown"),
        "heating_system": "unknown - requires supplemental data source",
        "cooling_system": "unknown - requires supplemental data source",
        "insulation_quality": "unknown",
        "energy_star_score": None,
        "estimated_annual_energy_use_mmbtu": None,
        "estimated_annual_co2e_tons": None,
        "estimated_annual_utility_cost_usd": None,
        "source": {
            "dataset": "NYC PLUTO",
            "dataset_id": PLUTO_DATASET,
            "record_url": "https://data.cityofnewyork.us/Housing-Development/MapPLUTO-2024-v2/64uk-42ks",
        },
    }


def _safe_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None
