from typing import Optional
from opentelemetry.semconv_ai import TraceloopSpanKindValues
from .base import _create_entity_method

def workflow(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
):
    """Keywords AI workflow decorator"""
    return _create_entity_method(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.WORKFLOW
    )

def task(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
):
    """Keywords AI task decorator"""
    return _create_entity_method(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.TASK
    )
