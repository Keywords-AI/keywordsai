from typing import Any
from typing import Dict
from typing import Optional
from typing import TypedDict


class RespanExportParams(TypedDict, total=False):
    disable_log: bool

    workflow_name: str
    span_name: str
    log_type: str

    trace_unique_id: str
    trace_id: str
    trace_name: str

    span_unique_id: str
    span_id: str
    span_parent_id: str
    parent_span_id: str

    session_identifier: str
    customer_identifier: str

    metadata: Dict[str, Any]


Payload = Dict[str, Any]
ValidatedPayload = Dict[str, Any]


InputValue = Any
OutputValue = Any
ErrorMessage = Optional[str]

