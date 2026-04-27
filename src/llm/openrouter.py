from __future__ import annotations

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _openrouter_client() -> OpenAI | None:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


def _llm_enabled() -> bool:
    return _openrouter_client() is not None


def _fallback_mode() -> str:
    # Supported: fallback_mock, fail_fast, human_prompt
    return os.getenv("LLM_FAILURE_MODE", "fallback_mock").strip().lower()


def refine_node_output(agent_name: str, state: Dict[str, Any], draft_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Best-effort refinement of draft node output with OpenRouter.
    Returns draft output when model is unavailable or fails and fallback mode is enabled.
    """
    if not _llm_enabled():
        return draft_output

    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto").strip() or "openrouter/auto"
    client = _openrouter_client()
    if client is None:
        return draft_output

    system_prompt = (
        "You are refining a JSON output for an energy-equity planning agent. "
        "Return STRICT JSON only. Keep the same top-level keys. "
        "Do not invent legal, emissions, or financial numbers. "
        "If uncertain, preserve original values. Keep citations URLs intact."
    )
    user_prompt = (
        f"Agent: {agent_name}\n"
        f"Current state (truncated): {json.dumps(_safe_state(state), ensure_ascii=True)}\n"
        f"Draft output JSON: {json.dumps(draft_output, ensure_ascii=True)}\n\n"
        "Task: minimally improve clarity and consistency while preserving schema and safety constraints."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = response.choices[0].message.content or ""
        refined = json.loads(text)
        if isinstance(refined, dict):
            return _merge_safe(draft_output, refined)
        return draft_output
    except Exception as exc:
        mode = _fallback_mode()
        if mode == "fail_fast":
            raise RuntimeError(f"OpenRouter refinement failed for {agent_name}: {exc}") from exc
        if mode == "human_prompt":
            updated = dict(draft_output)
            questions = list(updated.get("missing_data_questions", []))
            questions.append(
                "Model refinement unavailable. Please confirm whether to proceed with deterministic plan output."
            )
            updated["missing_data_questions"] = questions
            updated["next_step"] = "human_input"
            return updated
        return draft_output


def _safe_state(state: Dict[str, Any]) -> Dict[str, Any]:
    # Keep prompt small and avoid leaking large arrays.
    keys = ["building_data", "compliance_status", "available_grants", "proposed_solutions", "next_step"]
    trimmed = {k: state.get(k) for k in keys if k in state}
    return trimmed


def _merge_safe(original: Dict[str, Any], refined: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(original)
    for key, value in refined.items():
        if key in original:
            merged[key] = value
    return merged
