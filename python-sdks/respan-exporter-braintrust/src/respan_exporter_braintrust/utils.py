"""Utility functions for Braintrust exporter.

This module contains helper functions for:
- Type coercion (coerce_int, coerce_str)
- ID formatting (format_id)
- Timestamp formatting (format_timestamp)
- JSON sanitization (sanitize_json, json_dumps_safe)
- Token usage extraction (extract_token_usage, compute_total_request_tokens)
"""

import datetime
import json
import math
import uuid
from typing import Any, Dict, Optional, Set, Tuple


# =============================================================================
# Type Coercion Utilities
# =============================================================================


def coerce_int(value: Any) -> Optional[int]:
    """Coerce a value to an integer if possible.

    Args:
        value: The value to coerce.

    Returns:
        The integer value, or None if coercion fails.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def coerce_str(value: Any) -> Optional[str]:
    """Coerce a value to a string if possible.

    Args:
        value: The value to coerce.

    Returns:
        The string value, or None if coercion fails.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    return None


# =============================================================================
# ID Formatting Utilities
# =============================================================================


def format_id(value: Any) -> Optional[str]:
    """Format an ID value to a consistent string format.

    Converts UUIDs to hex strings (without dashes), passes through
    other string values, and converts integers to strings.

    Args:
        value: The ID value to format.

    Returns:
        The formatted ID string, or None if value is None/bool.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, uuid.UUID):
        return value.hex
    if isinstance(value, str):
        try:
            return uuid.UUID(value).hex
        except ValueError:
            return value
    if isinstance(value, int):
        return str(value)
    return str(value)


# =============================================================================
# Timestamp Formatting Utilities
# =============================================================================


def format_timestamp(value: Any) -> Optional[str]:
    """Format a timestamp to ISO 8601 format in UTC.

    Args:
        value: A Unix timestamp (int/float) or datetime object.

    Returns:
        ISO 8601 formatted string in UTC, or None if format fails.
    """
    if isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(
            value,
            tz=datetime.timezone.utc,
        ).isoformat()
    if isinstance(value, datetime.datetime):
        return value.astimezone(datetime.timezone.utc).isoformat()
    return None


# =============================================================================
# JSON Sanitization Utilities
# =============================================================================


def sanitize_json(value: Any, seen: Optional[Set[int]] = None) -> Any:
    """Recursively sanitize a value for JSON serialization.

    Handles:
    - Non-finite floats (NaN, Inf) -> None
    - datetime objects -> ISO 8601 strings
    - bytes -> UTF-8 decoded strings
    - Circular references -> "[CYCLE]" marker

    Args:
        value: The value to sanitize.
        seen: Set of object IDs already visited (for cycle detection).

    Returns:
        A JSON-serializable version of the value.
    """
    if seen is None:
        seen = set()

    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return value
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, datetime.datetime):
        return value.astimezone(datetime.timezone.utc).isoformat()
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="replace")
        except Exception:
            return str(value)

    if isinstance(value, dict):
        object_id = id(value)
        if object_id in seen:
            return "[CYCLE]"
        seen.add(object_id)
        return {str(k): sanitize_json(v, seen=seen) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        object_id = id(value)
        if object_id in seen:
            return ["[CYCLE]"]
        seen.add(object_id)
        return [sanitize_json(v, seen=seen) for v in value]
    return str(value)


def json_dumps_safe(value: Any) -> str:
    """Safely serialize a value to JSON string.

    Args:
        value: The value to serialize.

    Returns:
        JSON string representation of the sanitized value.
    """
    return json.dumps(sanitize_json(value), ensure_ascii=False)


# =============================================================================
# Token Usage Utilities
# =============================================================================


def extract_token_usage(record: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
    """Extract prompt and completion token counts from a Braintrust record.

    Searches in multiple locations:
    1. metrics.prompt_tokens / metrics.completion_tokens
    2. metrics.input_tokens / metrics.output_tokens
    3. metrics.usage or metrics.tokens
    4. metadata.prompt_tokens / metadata.completion_tokens
    5. metadata.usage or metadata.token_usage

    Args:
        record: The Braintrust log record.

    Returns:
        Tuple of (prompt_tokens, completion_tokens), either may be None.
    """
    def read_tokens(source: Any) -> Tuple[Optional[int], Optional[int]]:
        if not isinstance(source, dict):
            return None, None

        prompt = coerce_int(source.get("prompt_tokens"))
        completion = coerce_int(source.get("completion_tokens"))
        if prompt is None and completion is None:
            prompt = coerce_int(source.get("input_tokens"))
            completion = coerce_int(source.get("output_tokens"))

        return prompt, completion

    metrics = record.get("metrics")
    prompt_tokens, completion_tokens = read_tokens(metrics)
    if prompt_tokens is None and completion_tokens is None and isinstance(metrics, dict):
        usage = metrics.get("usage") or metrics.get("tokens")
        prompt_tokens, completion_tokens = read_tokens(usage)

    if prompt_tokens is None and completion_tokens is None:
        metadata = record.get("metadata")
        prompt_tokens, completion_tokens = read_tokens(metadata)
        if prompt_tokens is None and completion_tokens is None and isinstance(metadata, dict):
            usage = metadata.get("usage") or metadata.get("token_usage")
            prompt_tokens, completion_tokens = read_tokens(usage)

    return prompt_tokens, completion_tokens


def compute_total_request_tokens(
    prompt_tokens: Optional[int],
    completion_tokens: Optional[int],
) -> Optional[int]:
    """Compute total request tokens from prompt and completion tokens.

    Args:
        prompt_tokens: Number of prompt tokens, or None.
        completion_tokens: Number of completion tokens, or None.

    Returns:
        Sum of tokens, or None if both inputs are None.
    """
    if prompt_tokens is None and completion_tokens is None:
        return None
    return (prompt_tokens or 0) + (completion_tokens or 0)
