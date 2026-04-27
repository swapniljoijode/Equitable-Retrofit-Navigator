-- Audit event storage for Equitable Retrofit Navigator
-- Apply in Supabase SQL editor or migration workflow.

create extension if not exists pgcrypto;

create table if not exists public.workflow_audit_events (
  id uuid primary key default gen_random_uuid(),
  timestamp timestamptz not null,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_workflow_audit_events_timestamp
  on public.workflow_audit_events (timestamp desc);

create index if not exists idx_workflow_audit_events_event_type
  on public.workflow_audit_events (event_type);

create index if not exists idx_workflow_audit_events_payload_request_id
  on public.workflow_audit_events ((payload->>'request_id'));

alter table public.workflow_audit_events enable row level security;

-- Server-side writes should use service role key.
-- Deny broad public access by default.
revoke all on public.workflow_audit_events from anon;
revoke all on public.workflow_audit_events from authenticated;

-- Optional read-only policy for authenticated internal dashboard users.
drop policy if exists "Allow authenticated read audit events"
  on public.workflow_audit_events;

create policy "Allow authenticated read audit events"
  on public.workflow_audit_events
  for select
  to authenticated
  using (true);
