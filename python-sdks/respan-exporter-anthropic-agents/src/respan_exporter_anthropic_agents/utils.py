"""Utility helpers for Anthropic Agent SDK exporter."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from respan_sdk.constants.tracing_constants import (
    RESPAN_TRACING_INGEST_ENDPOINT,
    resolve_tracing_ingest_endpoint,
)


def resolve_export_endpoint(base_url: Optional[str]) -> str:
    """Resolve tracing ingest endpoint from a base URL or full ingest URL."""
    if not base_url:
        return RESPAN_TRACING_INGEST_ENDPOINT
    return resolve_tracing_ingest_endpoint(base_url=base_url)


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def coerce_int(value: Any) -> Optional[int]:
    """Convert value to int if possible."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_trace_name_from_prompt(prompt: Any) -> Optional[str]:
    """Create a readable trace name from user prompt text."""
    if not isinstance(prompt, str):
        return None
    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        return None
    return cleaned_prompt[:120]


def serialize_value(value: Any) -> Any:
    """Convert complex payload values into JSON-serializable structures."""
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        normalized_dictionary: Dict[str, Any] = {}
        for key, nested_value in value.items():
            normalized_dictionary[str(key)] = serialize_value(value=nested_value)
        return normalized_dictionary

    if isinstance(value, (list, tuple, set)):
        normalized_list: List[Any] = []
        for nested_value in value:
            normalized_list.append(serialize_value(value=nested_value))
        return normalized_list

    if hasattr(value, "__dict__"):
        return serialize_value(value=value.__dict__)

    return str(value)


def serialize_metadata(value: Any) -> Optional[Dict[str, Any]]:
    """Normalize metadata field for Respan payload."""
    serialized_value = serialize_value(value=value)
    if serialized_value is None:
        return None
    if isinstance(serialized_value, dict):
        return serialized_value
    return {"value": serialized_value}


def serialize_tool_calls(value: Any) -> Optional[List[Dict[str, Any]]]:
    """Normalize tool calls into list[dict]."""
    serialized_value = serialize_value(value=value)
    if serialized_value is None:
        return None
    if isinstance(serialized_value, list):
        normalized_list: List[Dict[str, Any]] = []
        for item in serialized_value:
            if isinstance(item, dict):
                normalized_list.append(item)
            else:
                normalized_list.append({"value": item})
        return normalized_list
    if isinstance(serialized_value, dict):
        return [serialized_value]
    return [{"value": serialized_value}]


def extract_session_id_from_system_message(system_message: Any) -> Optional[str]:
    """Extract session id from a SystemMessage payload."""
    system_data = getattr(system_message, "data", None) or {}
    raw_session_id = (
        system_data.get("session_id")
        or system_data.get("sessionId")
        or system_data.get("id")
    )
    if raw_session_id:
        return str(raw_session_id)
    return None
