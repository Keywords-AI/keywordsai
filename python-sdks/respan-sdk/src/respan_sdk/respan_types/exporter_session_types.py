"""Session state models for respan exporters (e.g. Anthropic Agent SDK)."""

from datetime import datetime
from typing import Any, Dict

from pydantic import Field

from respan_sdk.respan_types.base_types import RespanBaseModel


class PendingToolState(RespanBaseModel):
    """State for a tool span between PreToolUse and PostToolUse."""

    span_unique_id: str
    started_at: datetime
    tool_name: str
    tool_input: Any = None


class ExporterSessionState(RespanBaseModel):
    """
    Session state for exporter hooks: trace id, root span emission, pending tools.

    Use this instead of raw Dict[str, Any] for type-safe attribute access.
    """

    session_id: str
    trace_id: str
    trace_name: str
    started_at: datetime
    pending_tools: Dict[str, PendingToolState] = Field(default_factory=dict)
    is_root_emitted: bool = False
    prompt: Any = None
