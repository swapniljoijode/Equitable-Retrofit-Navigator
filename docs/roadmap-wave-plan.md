# Roadmap: 50/75/90/100

## 50% - Real Data

- Replace mock building profile with NYC Open Data PLUTO fetcher.
- Add data-quality normalization for missing/legacy fields.

## 75% - Digital Twin

- Add `simulation_node` to estimate 12-month energy outcomes.
- Use NYC weather history and measure-level performance assumptions.

## 90% - Human Approval

- Insert a human approval gate before grant submission.
- Provide Streamlit UI for consultant approval and override notes.

## 100% - Production

- Containerize with Docker.
- Add infrastructure as code deployment path (Lambda/ECS).
- Add observability, retries, and queue-based job processing.
