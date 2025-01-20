from functools import wraps
from typing import Optional
from opentelemetry.semconv_ai import TraceloopSpanKindValues
from traceloop.sdk.decorators import workflow as traceloop_workflow, task as traceloop_task

def _create_entity_method(
    name: Optional[str] = None,
    version: Optional[int] = None,
    tlp_span_kind: TraceloopSpanKindValues = TraceloopSpanKindValues.TASK,
    method_name: Optional[str] = None,
):
    """Base implementation for both workflow and task decorators"""
    if method_name is None:
        # Function decorator
        return traceloop_workflow(
            name=name,
            version=version,
            tlp_span_kind=tlp_span_kind
        )
    else:
        # Class method decorator
        return traceloop_workflow(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind
        )
