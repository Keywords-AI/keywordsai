"""Type definitions for Keywords AI Agno exporter."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class TraceContext:
    """Context information for a trace, extracted from trace object and root span."""

    trace_id: str
    trace_name: Optional[str]
    workflow_name: Optional[str]
    metadata: Dict[str, Any]
    session_identifier: Optional[Union[str, int]] = None
    trace_group_identifier: Optional[Union[str, int]] = None
    start_time: Optional[datetime] = None
    customer_identifier: Optional[Union[str, int]] = None


@dataclass
class SpanData:
    """Normalized span data extracted from various span formats."""

    span_id: str
    parent_id: Optional[str]
    name: Optional[str]
    span_kind: Optional[str]
    span_path: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    input_value: Any
    output_value: Any
    model: Optional[str]
    usage: Optional[Dict[str, Any]]
    error: Optional[str]
    status_code: Optional[int]
    metadata: Dict[str, Any]
    prompt_messages: Optional[List[Dict[str, Any]]]
    completion_message: Optional[Dict[str, Any]]
    tool_name: Optional[str]
    cost: Optional[float]
    latency: Optional[float]
