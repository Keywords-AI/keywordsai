from typing import Optional, Callable
from opentelemetry import context as context_api
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan
from opentelemetry.context import Context
from opentelemetry.semconv_ai import SpanAttributes
from keywordsai_sdk.keywordsai_types.span_types import KeywordsAISpanAttributes

from keywordsai_tracing.constants.generic import SDK_PREFIX


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
        # Add workflow name if present in context
        workflow_name = context_api.get_value("keywordsai_workflow_name")
        if workflow_name:
            span.set_attribute(SpanAttributes.TRACELOOP_WORKFLOW_NAME, workflow_name)

        # Add entity path if present in context
        entity_path = context_api.get_value("keywordsai_entity_path")
        if entity_path:
            span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_PATH, entity_path)

        # Add trace group identifier if present
        trace_group_id = context_api.get_value("keywordsai_trace_group_identifier")
        if trace_group_id:
            span.set_attribute(
                KeywordsAISpanAttributes.KEYWORDSAI_TRACE_GROUP_ID.value, trace_group_id
            )

        # Add custom parameters if present
        keywordsai_params = context_api.get_value("keywordsai_params")
        if keywordsai_params and isinstance(keywordsai_params, dict):
            for key, value in keywordsai_params.items():
                span.set_attribute(f"{SDK_PREFIX}.{key}", value)

        # Call original processor's on_start
        self.processor.on_start(span, parent_context)

    def on_end(self, span: ReadableSpan):
        """Called when a span ends"""
        self.processor.on_end(span)

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
