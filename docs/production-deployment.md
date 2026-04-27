# Production Deployment Guide

## Runtime Topology

- FastAPI service in container (`app/api.py`) for synchronous orchestration calls.
- ECS Fargate for always-on API.
- Optional Lambda (container image) for event-driven or batch triggers.

## Recommended Production Additions

1. Application Load Balancer + HTTPS termination.
2. API Gateway (if exposing Lambda path).
3. Secrets Manager for API keys and tokens.
4. Autoscaling policies for ECS service.
5. Structured observability (CloudWatch + tracing).

## Security Baseline

- No secrets in repo.
- Restrict IAM roles to least privilege.
- Keep private subnets and controlled egress.
- `/run` now requires `X-API-Key` header matching `API_AUTH_KEY`.
- Terminate TLS at ALB and keep ECS service in private subnets.
- WAF with managed rules + IP rate limiting should be enabled for internet-facing traffic.
- Audit logs should be retained for consultant approvals and citation traceability.
- Use `X-Request-ID` for end-to-end correlation in API, gateway, and storage logs.
- Optional: persist audit events into Supabase table `workflow_audit_events` via service role key.
