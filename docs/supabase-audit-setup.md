# Supabase Audit Setup

This project can persist structured workflow audit events to Supabase.

## 1) Required Environment Variables

Set these in runtime environment (local `.env` and production secrets):

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_AUDIT_TABLE=workflow_audit_events`

## 2) Apply SQL Migrations

Run in Supabase SQL editor (in order):

1. `db/migrations/001_workflow_audit_events.sql`
2. `db/migrations/002_workflow_audit_retention.sql`

## 3) Smoke Test Insert Path

Start API and make a request to `/run` with valid API key.
Then check:

```sql
select timestamp, event_type, payload->>'request_id' as request_id
from public.workflow_audit_events
order by timestamp desc
limit 20;
```

## 4) Optional Scheduled Retention

Retention function:

```sql
select audit_private.prune_workflow_audit_events(90);
```

You can schedule this daily via Supabase cron or any external scheduler.
