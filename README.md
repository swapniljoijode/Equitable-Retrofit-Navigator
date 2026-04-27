# Equitable Retrofit Navigator

Equitable Retrofit Navigator is a LangGraph-based multi-agent system for planning affordable-housing retrofits in NYC with LL97 compliance and energy-equity guardrails.

## Phase 1 Scope

- Multi-agent orchestration with a stateful LangGraph pipeline.
- Initial agents:
  - `Compliance_Scout`
  - `Data_Auditor`
  - `Incentive_Hunter`
  - `Retrofit_Architect`
  - `Equity_Manager`
- Reflection loops:
  - If grants are unavailable, trigger a lower-cost re-plan path.
  - If resident bill reduction is below 15%, re-plan until threshold or human input is required.
  - `simulation_node` runs a 12-month proxy projection before final equity validation.

## Quick Start

1. Create environment:
   - `python -m venv .venv`
   - `.venv\Scripts\activate` (Windows PowerShell)
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run:
   - `python -m src.main`

### Human Approval Dashboard

- Launch:
  - `streamlit run app/approval_dashboard.py`
- Use this to set consultant approval state (`pending`, `approved`, `rejected`) before the incentive workflow branch.

### API Service (Production Runtime)

- Local API run:
  - `uvicorn app.api:app --reload --host 0.0.0.0 --port 8000`
- Health check:
  - `GET /health`
- Workflow execution:
  - `POST /run`
  - Include header: `X-API-Key: <API_AUTH_KEY>`

### Docker

- Build:
  - `docker build -t equitable-retrofit-navigator .`
- Run:
  - `docker run --rm -p 8000:8000 equitable-retrofit-navigator`

### Terraform (AWS)

- Infra files are in `infra/terraform`.
- See `infra/terraform/README.md` for `init/plan/apply` flow.
- Terraform now provisions ALB HTTPS listener, ECS service target group wiring, and Secrets Manager-backed env injection.

### Automated Tests

- Run:
  - `pytest -q`
- Acceptance checklist:
  - `docs/acceptance-test-checklist.md`

### Audit Logging

- API emits structured JSON audit events:
  - `workflow_run_requested`
  - `workflow_run_completed`
- Events include approval state and citation summary for traceability.
- API emits/returns `X-Request-ID` for correlation across logs and clients.
- Optional Supabase sink:
  - set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_AUDIT_TABLE`.
  - apply SQL setup in `docs/supabase-audit-setup.md`

### Release Command

- PowerShell one-command preflight + build:
  - `.\scripts\release.ps1`
- Skip Docker build:
  - `.\scripts\release.ps1 -SkipDocker`

### Data Sources

- Mock mode (default):
  - `python -m src.main --source mock`
- NYC PLUTO mode (live pull by BBL):
  - `python -m src.main --source pluto --bbl 2030400050`
- NYC PLUTO mode (live pull by BIN):
  - `python -m src.main --source pluto --bin 2112345`

Optional: set `NYC_OPEN_DATA_APP_TOKEN` in your environment for better Open Data API limits.
Note: PLUTO runs are automatically enriched with low-confidence proxy energy/cost/emissions estimates for planning continuity.

## Project Layout

- `src/state.py` - shared graph state contract.
- `src/agents.py` - node logic and structured outputs.
- `src/graph.py` - LangGraph construction and conditional routing.
- `src/main.py` - execution entrypoint.
- `src/tools/nyc_pluto.py` - PLUTO API fetch + normalization helper.
- `src/tools/energy_enrichment.py` - proxy enrichment for missing energy/carbon/cost fields.
- `data/building_profile.json` - Bronx mock building profile.
- `.cursor/rules/` - persistent coding and safety rules.
- `.cursor/hooks/` - hook scripts for shell safety.
- `.cursor/skills/` - project-specific Cursor skill definitions.

## Guardrails

- Do not invent legal or financial values.
- Include source citations for law and grants whenever available.
- If required data is missing, ask the human user before continuing.

## OpenRouter Model Setup

- Add `OPENROUTER_API_KEY` to your local `.env`.
- Default model is `OPENROUTER_MODEL=openrouter/auto`.
- Failure mode is configurable:
  - `LLM_FAILURE_MODE=fallback_mock` (recommended; deterministic fallback)
  - `LLM_FAILURE_MODE=fail_fast`
  - `LLM_FAILURE_MODE=human_prompt`
