# Acceptance Test Checklist

Use this checklist before marking a milestone as complete.

## 1) Environment Setup

- [ ] `python -m venv .venv` created
- [ ] dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` exists with `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `LLM_FAILURE_MODE`, `API_AUTH_KEY`

## 2) Core Graph Behavior

- [ ] Pending human approval pauses with `next_step: human_input`
  - Command: `python -m src.main --source mock`
- [ ] Approved flow reaches `next_step: done`
  - Use Streamlit or API with `human_approval=approved`
- [ ] No grants branch triggers replan route for retrofit architect
- [ ] Equity threshold (<15%) triggers reflection loop

## 3) Data Ingestion

- [ ] Mock data run succeeds (`--source mock`)
- [ ] PLUTO run succeeds (`--source pluto --bbl <id>` or `--bin <id>`)
- [ ] Missing PLUTO fields produce human questions, not hallucinated values

## 4) Simulation and Equity

- [ ] `simulation_report` includes 12 monthly entries
- [ ] `annual_savings_mmbtu` is present
- [ ] `affordability_passed` is computed

## 5) API and Security

- [ ] `GET /health` returns `200`
- [ ] `POST /run` without `X-API-Key` returns `401`
- [ ] `POST /run` with valid `X-API-Key` returns `200`

## 6) Automated Tests

- [ ] Run unit tests: `pytest -q`
- [ ] Ensure both graph-path and auth tests pass

## 7) Container and Infra

- [ ] Docker image builds: `docker build -t equitable-retrofit-navigator .`
- [ ] Container starts and health endpoint works
- [ ] Terraform validates: `terraform -chdir=infra/terraform init && terraform -chdir=infra/terraform validate`

## 8) Production Readiness Signoff

- [ ] Secrets configured in environment and/or cloud secret manager
- [ ] CI pipeline green on latest commit
- [ ] Deployment endpoint reachable behind TLS
- [ ] Audit trail includes citations for law/grant references
