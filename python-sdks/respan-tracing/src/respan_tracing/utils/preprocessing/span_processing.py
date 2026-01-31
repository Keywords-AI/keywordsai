from typing import Optional
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv_ai import SpanAttributes
import logging

logger = logging.getLogger(__name__)


def should_process_span(span: ReadableSpan) -> bool:
    """
    Determine if a span should be processed based on KeywordsAI/Traceloop attributes.
    
    Logic:
    - If span has TRACELOOP_SPAN_KIND: it's a user-decorated span → process
    - If span has TRACELOOP_ENTITY_PATH: it's a child span within entity context → process  
    - If span has neither: it's auto-instrumentation noise → filter out
    
    Args:
        span: The span to evaluate
        
    Returns:
        bool: True if span should be processed, False if it should be filtered out
    """
    span_kind = span.attributes.get(SpanAttributes.TRACELOOP_SPAN_KIND)
    entity_path = span.attributes.get(SpanAttributes.TRACELOOP_ENTITY_PATH, "")
    
    # User-decorated span (has TRACELOOP_SPAN_KIND)
    if span_kind:
        logger.debug(
            f"[KeywordsAI Debug] Processing user-decorated span: {span.name} (kind: {span_kind})"
        )
        return True
    
    # Child span within entity context (has TRACELOOP_ENTITY_PATH)
    elif entity_path and entity_path != "":
        logger.debug(
            f"[KeywordsAI Debug] Processing child span within entity context: {span.name} (entityPath: {entity_path})"
        )
        return True
    
    # Auto-instrumentation noise - filter out
    else:
        logger.debug(
            f"[KeywordsAI Debug] Filtering out auto-instrumentation span: {span.name} (no TRACELOOP_SPAN_KIND or entityPath)"
        )
        return False


def should_make_root_span(span: ReadableSpan) -> bool:
    """
    Determine if a span should be converted to a root span.
    
    Logic:
    - User-decorated span (TRACELOOP_SPAN_KIND) without entity path should become root
    
    Args:
        span: The span to evaluate
        
    Returns:
        bool: True if span should be made a root span
    """
    span_kind = span.attributes.get(SpanAttributes.TRACELOOP_SPAN_KIND)
    entity_path = span.attributes.get(SpanAttributes.TRACELOOP_ENTITY_PATH, "")
    
    # User-decorated span without entity path should become root
    is_root_candidate = span_kind is not None and (not entity_path or entity_path == "")
    
    if is_root_candidate:
        logger.debug(f"[KeywordsAI Debug] Span should be made root: {span.name}")
    
    return is_root_candidate
