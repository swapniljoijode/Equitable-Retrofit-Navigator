from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from src.audit_store import persist_audit_event


logger = logging.getLogger("retrofit_audit")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def emit_audit_event(event_type: str, payload: Dict[str, Any]) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload,
    }
    logger.info(json.dumps(record, ensure_ascii=True))
    persist_audit_event(record)


def summarize_citations(citations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [
        {
            "source_type": c.get("source_type", ""),
            "reference": c.get("reference", ""),
            "url": c.get("url", ""),
        }
        for c in citations
    ]
