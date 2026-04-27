# NYC Open Data Integration (PLUTO)

## Current Implementation

- Added `src/tools/nyc_pluto.py` for direct calls to NYC Open Data SODA endpoint.
- Added `src/tools/energy_enrichment.py` to fill missing planning fields with transparent, low-confidence proxies.
- Supports lookup by either:
  - `bbl` (borough-block-lot)
  - `bin` (building identification number)
- Added CLI switches in `src/main.py`:
  - `--source pluto`
  - `--bbl <value>` or `--bin <value>`

## Important Data Caveats

PLUTO does not provide all energy-specific fields needed for full retrofit modeling. The system now injects proxy values for continuity, marked with `proxy_estimates` metadata:

- heating and cooling system specifics
- annual utility cost
- annual CO2e emissions
- annual energy use

The graph still prompts for human validation because these are not official utility or benchmarking values.

## Next Upgrade

- Join PLUTO with additional datasets (e.g., benchmarking/energy grades) to replace proxy values with source-backed measurements.
