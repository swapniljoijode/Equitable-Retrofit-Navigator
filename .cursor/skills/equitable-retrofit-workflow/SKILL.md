---
name: equitable-retrofit-workflow
description: Build and evolve the Equitable Retrofit Navigator agentic workflow for NYC affordable housing compliance and retrofit planning. Use when implementing LL97 logic, incentives workflows, retrofit calculations, affordability checks, and human-in-the-loop controls.
---

# Equitable Retrofit Workflow

## Purpose

Maintain a modular, stateful LangGraph pipeline that prioritizes:

1. LL97 compliance insight
2. Incentive discovery
3. Retrofit feasibility
4. Resident affordability and comfort

## Workflow Steps

1. Validate incoming building data.
2. Run compliance analysis with explicit assumptions.
3. Search and attach available incentives with links.
4. Generate retrofit options with cost and CO2 impacts.
5. Enforce equity threshold (minimum 15% bill reduction).
6. If threshold fails, trigger re-plan loop or request human input.

## Output Contract

Every node returns structured JSON containing:

- updated state fields
- `next_step`
- `missing_data_questions` when needed
- `citations` for policy or grants

## Guardrails

- Never fabricate legal or grant details.
- Mark all mock values as placeholders.
- Ask for missing critical fields before final recommendations.
