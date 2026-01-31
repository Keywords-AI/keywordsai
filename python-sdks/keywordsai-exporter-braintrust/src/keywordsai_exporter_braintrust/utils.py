import datetime
import json
import math
import uuid
from typing import Any, Dict, Optional, Tuple


def coerce_int(value: Any) -> Optional[int]:
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
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    return None


def format_id(value: Any) -> Optional[str]:
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


def format_timestamp(value: Any) -> Optional[str]:
    if isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(
            value,
            tz=datetime.timezone.utc,
        ).isoformat()
    if isinstance(value, datetime.datetime):
        return value.astimezone(datetime.timezone.utc).isoformat()
    return None


def sanitize_json(value: Any, seen: Optional[set[int]] = None) -> Any:
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
    return json.dumps(sanitize_json(value), ensure_ascii=False)


def extract_token_usage(record: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
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
    if prompt_tokens is None and completion_tokens is None:
        return None
    return (prompt_tokens or 0) + (completion_tokens or 0)

