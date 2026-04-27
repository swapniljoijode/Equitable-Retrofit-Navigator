# Connector Setup Notes

## Cursor + Claude Code

- Keep `.cursor/rules/`, `.cursor/hooks.json`, and `.cursor/skills/` under version control.
- Use project hooks for shared safety controls.
- Store secrets only in local environment files, never in git.

## Supabase (Free Tier)

1. Create a Supabase project.
2. Copy URL and anon key into local `.env`.
3. Enable Row Level Security on all exposed tables.
4. Keep privileged operations on backend-only paths.

## Notion Workspace

- Use Notion MCP for grant/program research tracking and delivery notes.
- For any automated task/page writes, authenticate the Notion connector before use.

## Integration Policy

- Treat all external connectors as optional until authenticated.
- If a connector is unavailable, continue with mock mode and explicit TODO markers.
