from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict


def persist_audit_event(event: Dict[str, Any]) -> None:
    """
    Best-effort audit persistence into Supabase via PostgREST.
    No-op when config is missing.
    """
    base_url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    table = os.getenv("SUPABASE_AUDIT_TABLE", "workflow_audit_events").strip()

    if not base_url or not service_key:
        return

    url = f"{base_url}/rest/v1/{table}"
    payload = json.dumps(event).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=payload,
        method="POST",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=8):
            pass
    except (urllib.error.URLError, urllib.error.HTTPError):
        # Keep API path non-blocking if audit sink is unavailable.
        return
