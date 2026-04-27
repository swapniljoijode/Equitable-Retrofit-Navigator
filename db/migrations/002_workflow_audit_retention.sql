-- Retention helper for audit records.
-- Keeps latest N days of events and deletes older rows.
-- Schedule via Supabase pg_cron, external scheduler, or manual run.
-- Security definer is placed in a non-exposed schema.

create schema if not exists audit_private;

create or replace function audit_private.prune_workflow_audit_events(retain_days integer default 90)
returns integer
language plpgsql
security definer
as $$
declare
  deleted_count integer;
begin
  delete from public.workflow_audit_events
  where timestamp < (now() - make_interval(days => retain_days));

  get diagnostics deleted_count = row_count;
  return deleted_count;
end;
$$;

revoke all on function audit_private.prune_workflow_audit_events(integer) from public;
grant execute on function audit_private.prune_workflow_audit_events(integer) to service_role;
