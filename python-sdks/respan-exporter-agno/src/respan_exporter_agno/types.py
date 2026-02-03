"""Type definitions for Respan Agno exporter."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union


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
