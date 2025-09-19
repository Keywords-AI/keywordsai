from typing import Optional, Callable, Dict, Any
from opentelemetry import context as context_api
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan
from opentelemetry.context import Context
from opentelemetry.semconv_ai import SpanAttributes
from keywordsai_sdk.keywordsai_types.span_types import KeywordsAISpanAttributes
import logging

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
