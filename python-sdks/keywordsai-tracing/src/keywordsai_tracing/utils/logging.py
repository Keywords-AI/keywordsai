"""
Logging utilities for KeywordsAI tracing.

This module provides a consistent way to create child loggers that properly
inherit from the main KeywordsAI logger, avoiding the confusing dependency
on __name__ matching the logger prefix.
"""

import json
import logging
from keywordsai_tracing.constants.generic_constants import LOGGER_NAME
from typing import Any, Dict, List
from opentelemetry.trace import SpanContext

from keywordsai_tracing.constants.keywordsai_config import (
    HIGHLIGHTED_ATTRIBUTE_KEY_SUBSTRINGS,
)


def get_keywordsai_logger(name: str) -> logging.Logger:
    """
    Create a child logger under the KeywordsAI logger hierarchy.

    This ensures proper inheritance regardless of the LOGGER_NAME value
    and makes the hierarchy explicit and intentional.

    Args:
        name: The child logger name (e.g., 'core.exporter', 'core.client')

    Returns:
        A logger that inherits from the main KeywordsAI logger

    Example:
        # In exporter.py
        from keywordsai_tracing.utils.logging import get_keywordsai_logger
        logger = get_keywordsai_logger('core.exporter')

        # In client.py
        logger = get_keywordsai_logger('core.client')
    """
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def get_main_logger() -> logging.Logger:
    """
    Get the main KeywordsAI logger.

    Returns:
        The main KeywordsAI logger instance
    """
    return logging.getLogger(LOGGER_NAME)


def _safe_value_for_preview(value: Any) -> Any:
    """Safely convert values for debug preview, truncating large content."""
    try:
        if isinstance(value, (bytes, bytearray)):
            return f"<bytes {len(value)}B>"
        if isinstance(value, (list, tuple)):
            return [str(item)[:500] for item in value]
        if isinstance(value, dict):
            return {str(k): str(v)[:500] for k, v in value.items()}
        s_val = str(value)
        return s_val if len(s_val) <= 1000 else s_val[:1000] + "...<truncated>"
    except Exception:
        return "<unserializable>"


def build_spans_export_preview(spans: List[Any]) -> List[Dict[str, Any]]:
    """
    Build a sanitized preview for spans about to be exported.

    Returns a list of dicts with name, ids, key attributes, and highlighted attributes.
    """
    preview: List[Dict[str, Any]] = []
    for s in spans:
        try:
            ctx: SpanContext = s.get_span_context()  # type: ignore[attr-defined]
            attrs: Dict[str, Any] = getattr(s, "attributes", {}) or {}

            highlighted_keys = [
                k
                for k in attrs.keys()
                if any(
                    x in str(k).lower() for x in HIGHLIGHTED_ATTRIBUTE_KEY_SUBSTRINGS
                )
            ]
            preview.append(
                {
                    "name": getattr(s, "name", "<unknown>"),
                    "trace_id": format(ctx.trace_id, "032x") if ctx else None,
                    "span_id": format(ctx.span_id, "016x") if ctx else None,
                    "parent_span_id": getattr(s._parent, "span_id", None),
                    "kind": attrs.get("traceloop.span.kind"),
                    "entity_path": attrs.get("traceloop.entity.path"),
                    "attributes_count": len(attrs),
                    "highlighted_attributes": {
                        str(k): _safe_value_for_preview(attrs.get(k))
                        for k in highlighted_keys
                    },
                }
            )
        except Exception as e:
            preview.append({"error": f"failed_to_preview_span: {e}"})

    return json.dumps(preview, indent=2, default=str)
