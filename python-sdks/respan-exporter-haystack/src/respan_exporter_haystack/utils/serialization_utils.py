"""Serialization helper utilities."""

import json
from typing import Any


def serialize_data(data: Any) -> str:
    """Serialize values for trace payload logging fields."""
    try:
        if isinstance(data, (str, int, float, bool)):
            return str(data)
        return json.dumps(data, default=str)
    except Exception:
        return str(data)
