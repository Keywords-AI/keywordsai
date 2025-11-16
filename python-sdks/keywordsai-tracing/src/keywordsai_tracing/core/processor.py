from typing import Optional, Callable, Dict, Any, List
from contextvars import ContextVar
import logging

from opentelemetry import context as context_api, trace
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.context import Context
from opentelemetry.semconv_ai import SpanAttributes

from keywordsai_sdk.keywordsai_types.span_types import KeywordsAISpanAttributes
from keywordsai_tracing.constants.generic_constants import SDK_PREFIX
from keywordsai_tracing.constants.context_constants import (
    TRACE_GROUP_ID_KEY, 
    PARAMS_KEY
)
from keywordsai_tracing.utils.preprocessing.span_processing import should_process_span
from keywordsai_tracing.utils.context import get_entity_path

logger = logging.getLogger(__name__)


class KeywordsAISpanProcessor:
    """
    Custom span processor that wraps the underlying processor and adds
    KeywordsAI-specific metadata to spans.
    """

    def __init__(
        self,
        processor: SpanProcessor,
        span_postprocess_callback: Optional[Callable[[ReadableSpan], None]] = None,
    ):
        self.processor = processor
        self.span_postprocess_callback = span_postprocess_callback

        # Store original on_end method if we have a callback
        if span_postprocess_callback:
            self.original_on_end = processor.on_end
            processor.on_end = self._wrapped_on_end

    def on_start(self, span, parent_context: Optional[Context] = None):
        """Called when a span is started - add KeywordsAI metadata"""
        # Check if this span is being created within an entity context
        # If so, add the entityPath attribute so it gets preserved by our filtering
        entity_path = get_entity_path(parent_context)  # Use active context like JS version
        if entity_path and not span.attributes.get(SpanAttributes.TRACELOOP_SPAN_KIND):
            # This is an auto-instrumentation span within an entity context
            # Add the entityPath attribute so it doesn't get filtered out
            logger.debug(
                f"[KeywordsAI Debug] Adding entityPath to auto-instrumentation span: {span.name} (entityPath: {entity_path})"
            )
            span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_PATH, entity_path)

        # Add workflow name if present in context
        workflow_name = context_api.get_value(SpanAttributes.TRACELOOP_ENTITY_NAME)
        if workflow_name:
            span.set_attribute(SpanAttributes.TRACELOOP_WORKFLOW_NAME, workflow_name)

        # Add entity path if present in context (for redundancy)
        entity_path_from_context = context_api.get_value(SpanAttributes.TRACELOOP_ENTITY_PATH)
        if entity_path_from_context:
            span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_PATH, entity_path_from_context)

        # Add trace group identifier if present
        trace_group_id = context_api.get_value(TRACE_GROUP_ID_KEY)
        if trace_group_id:
            span.set_attribute(
                KeywordsAISpanAttributes.KEYWORDSAI_TRACE_GROUP_ID.value, trace_group_id
            )

        # Add custom parameters if present
        keywordsai_params = context_api.get_value(PARAMS_KEY)
        if keywordsai_params and isinstance(keywordsai_params, dict):
            for key, value in keywordsai_params.items():
                span.set_attribute(f"{SDK_PREFIX}.{key}", value)

        # Call original processor's on_start
        self.processor.on_start(span, parent_context)

    def on_end(self, span: ReadableSpan):
        """Called when a span ends - filter spans based on KeywordsAI attributes"""
        # Apply filtering logic using shared function
        if should_process_span(span):
            self.processor.on_end(span)
        else:
            logger.debug(f"[KeywordsAI Debug] Skipping filtered span: {span.name}")

    def _wrapped_on_end(self, span: ReadableSpan):
        """Wrapped on_end method that calls custom callback first"""
        if self.span_postprocess_callback:
            self.span_postprocess_callback(span)
        self.original_on_end(span)

    def shutdown(self):
        """Shutdown the underlying processor"""
        return self.processor.shutdown()

    def force_flush(self, timeout_millis: int = 30000):
        """Force flush the underlying processor"""
        return self.processor.force_flush(timeout_millis)


# ============================================================================
# Buffering Span Processor - OTEL-compliant span buffering functionality
# ============================================================================


# Context variable to track the active SpanBuffer for the current context
_active_span_buffer: ContextVar[Optional['SpanBuffer']] = ContextVar(
    'active_span_buffer', default=None
)


class BufferingSpanProcessor(SpanProcessor):
    """
    OpenTelemetry-compliant span processor that can buffer spans when requested.
    
    This processor checks if there's an active SpanBuffer in the current context.
    If there is, spans go to that buffer's local queue. Otherwise, spans are
    passed through to the original processor for normal export.
    
    This follows OpenTelemetry patterns by using a single processor that can
    conditionally buffer spans based on context, rather than swapping processors.
    """
    
    def __init__(self, original_processor: SpanProcessor):
        """
        Initialize the buffering processor.
        
        Args:
            original_processor: The original processor to fall back to when
                              no active SpanBuffer is present
        """
        self.original_processor = original_processor
    
    def on_start(self, span, parent_context: Optional[Context] = None):
        """
        Called when a span starts.
        
        Forward to original processor (needed for proper span initialization).
        """
        self.original_processor.on_start(span, parent_context)
    
    def on_end(self, span: ReadableSpan):
        """
        Called when a span ends.
        
        If there's an active SpanBuffer in the current context, route the span
        to its local queue. Otherwise, pass through to the original processor.
        
        Args:
            span: The span that ended
        """
        # Check if there's an active SpanBuffer in this context
        buffer = _active_span_buffer.get()
        
        if buffer is not None and buffer._is_buffering:
            # Route to the buffer's local queue
            logger.debug(
                f"[SpanBuffer] Buffering span '{span.name}' "
                f"for trace {buffer.trace_id}"
            )
            buffer._local_queue.append(span)
        else:
            # No active buffer - use original processor (normal export)
            self.original_processor.on_end(span)
    
    def shutdown(self):
        """Shutdown the processor."""
        return self.original_processor.shutdown()
    
    def force_flush(self, timeout_millis: int = 30000):
        """Force flush the processor."""
        return self.original_processor.force_flush(timeout_millis)


class SpanBuffer:
    """
    OpenTelemetry-compliant context manager for buffering spans with manual export control.
    
    Uses context variables to ensure only spans created within this buffer's
    context are collected, without affecting other spans in the application.
    
    This follows OpenTelemetry patterns and avoids naming conflicts with 
    the OpenTelemetry Collector component.
    
    This enables:
    1. Batch buffering of multiple spans
    2. Manual export timing control
    3. Asynchronous span creation (create spans after execution completes)
    4. Single ingestion call per trace instead of per-span
    5. Thread-safe isolation (each context has its own buffer)
    """
    
    def __init__(self, trace_id: str, exporter: SpanExporter):
        """
        Initialize the span buffer.
        
        Args:
            trace_id: Trace ID for the spans being buffered
            exporter: SpanExporter to use for batch export
        """
        self.trace_id = trace_id
        self.exporter = exporter
        self._local_queue: List[ReadableSpan] = []
        self._is_buffering = False
        self._context_token = None
    
    def __enter__(self):
        """
        Enter context: Set this buffer as active in the current context.
        
        Spans created within this context will be routed to this buffer's
        local queue instead of being exported immediately.
        
        Returns:
            self for context manager usage
        """
        logger.debug(f"[SpanBuffer] Entering buffering context for trace {self.trace_id}")
        
        # Mark as buffering
        self._is_buffering = True
        
        # Set this buffer as active in the context variable
        self._context_token = _active_span_buffer.set(self)
        
        logger.debug(f"[SpanBuffer] Activated buffer for trace {self.trace_id}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context: Deactivate this buffer in the current context.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        logger.debug(f"[SpanBuffer] Exiting buffering context for trace {self.trace_id}")
        
        # Mark as not buffering
        self._is_buffering = False
        
        # Reset the context variable
        if self._context_token is not None:
            _active_span_buffer.reset(self._context_token)
            self._context_token = None
        
        logger.debug(f"[SpanBuffer] Deactivated buffer for trace {self.trace_id}")
        
        # Note: Local queue persists for manual export or inspection
        # It will be cleaned up by garbage collection when this object is destroyed
    
    def create_span(
        self, 
        span_name: str, 
        attributes: Optional[Dict[str, Any]] = None,
        kind: Optional[trace.SpanKind] = None
    ) -> str:
        """
        Create a span that goes to the local queue (not auto-exported).
        
        Args:
            span_name: Name of the span
            attributes: Optional attributes to set on the span
            kind: Optional span kind (default: INTERNAL)
        
        Returns:
            The span ID as a hex string
        """
        tracer = trace.get_tracer("keywordsai.span_buffer")
        
        # Set span kind
        span_kind = kind or trace.SpanKind.INTERNAL
        
        # Create span in context
        with tracer.start_as_current_span(span_name, kind=span_kind) as span:
            # Set trace ID if we can (note: trace_id is already set by the tracer)
            # We just use the provided trace_id for logging/tracking purposes
            
            # Set attributes
            if attributes:
                for key, value in attributes.items():
                    try:
                        span.set_attribute(key, value)
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"[SpanBuffer] Failed to set attribute {key}={value}: {e}"
                        )
            
            # Span goes to local queue when this context exits
            span_id = format(span.get_span_context().span_id, '016x')
            logger.debug(f"[SpanBuffer] Created span '{span_name}' with ID {span_id}")
            
        return span_id
    
    def get_all_spans(self) -> List[ReadableSpan]:
        """
        Get all spans from the local queue.
        
        Returns:
            List of all buffered spans
        """
        return self._local_queue.copy()
    
    def export_spans(self) -> bool:
        """
        Export all spans from the local queue as a single batch.
        
        Returns:
            True if export was successful, False otherwise
        """
        if not self._local_queue:
            logger.debug(f"[SpanBuffer] No spans to export for trace {self.trace_id}")
            return True
        
        logger.info(
            f"[SpanBuffer] Exporting {len(self._local_queue)} spans "
            f"for trace {self.trace_id}"
        )
        
        try:
            result = self.exporter.export(self._local_queue)
            success = result == SpanExportResult.SUCCESS
            
            if success:
                logger.info(
                    f"[SpanBuffer] Successfully exported {len(self._local_queue)} spans"
                )
            else:
                logger.error(
                    f"[SpanBuffer] Failed to export spans: {result}"
                )
            
            return success
            
        except Exception as e:
            logger.exception(f"[SpanBuffer] Exception during export: {e}")
            return False
    
    def clear_spans(self):
        """
        Clear all spans from the local queue without exporting.
        
        Useful for discarding buffered spans if you decide not to export them.
        """
        span_count = len(self._local_queue)
        self._local_queue.clear()
        logger.debug(f"[SpanBuffer] Cleared {span_count} spans from queue")
    
    def get_span_count(self) -> int:
        """
        Get the number of spans in the local queue.
        
        Returns:
            Number of buffered spans
        """
        return len(self._local_queue)
