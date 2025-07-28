from typing import Dict, Optional, Sequence, List
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import SpanContext
from ..utils.logging import get_keywordsai_logger
from ..utils.preprocessing.span_processing import should_make_root_span

logger = get_keywordsai_logger('core.exporter')


class ModifiedSpan:
    """A wrapper class to create a modified version of ReadableSpan with parent_span_id set to None"""
    
    def __init__(self, original_span: ReadableSpan):
        self._original_span = original_span
        # Create a new span context with no parent
        self._context = SpanContext(
            trace_id=original_span.context.trace_id,
            span_id=original_span.context.span_id,
            is_remote=original_span.context.is_remote,
            trace_flags=original_span.context.trace_flags,
            trace_state=original_span.context.trace_state
        )
    
    @property
    def name(self):
        return self._original_span.name
    
    @property
    def context(self):
        return self._context
    
    @property
    def parent_span_id(self):
        return None  # This is the key change - no parent
    
    @property
    def start_time(self):
        return self._original_span.start_time
    
    @property
    def end_time(self):
        return self._original_span.end_time
    
    @property
    def attributes(self):
        return self._original_span.attributes
    
    @property
    def events(self):
        return self._original_span.events
    
    @property
    def links(self):
        return self._original_span.links
    
    @property
    def status(self):
        return self._original_span.status
    
    @property
    def kind(self):
        return self._original_span.kind


class KeywordsAISpanExporter:
    """ 
    Custom span exporter for KeywordsAI that wraps the OTLP HTTP exporter
    with proper authentication and endpoint handling.
    """
    
    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        
        # Prepare headers for authentication
        export_headers = headers.copy() if headers else {}
        
        if api_key:
            export_headers["Authorization"] = f"Bearer {api_key}"
        
        # Ensure we're using the traces endpoint
        traces_endpoint = self._build_traces_endpoint(endpoint)
        logger.debug(f"Traces endpoint: {traces_endpoint}")
        # Initialize the underlying OTLP exporter
        self.exporter = OTLPSpanExporter(
            endpoint=traces_endpoint,
            headers=export_headers,
        )
    
    def _build_traces_endpoint(self, base_endpoint: str) -> str:
        """Build the proper traces endpoint URL"""
        # Remove trailing slash
        base_endpoint = base_endpoint.rstrip('/')
        
        # Add traces path if not already present
        if not base_endpoint.endswith('/v1/traces'):
            return f"{base_endpoint}/v1/traces"
        
        return base_endpoint
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to KeywordsAI, modifying spans to make user-decorated spans root spans where appropriate"""
        modified_spans: List[ReadableSpan] = []
        
        for span in spans:
            if should_make_root_span(span):
                logger.debug(f"[KeywordsAI Debug] Making span a root span: {span.name}")
                # Create a modified span with no parent
                modified_span = ModifiedSpan(span)
                modified_spans.append(modified_span)
            else:
                # Use the original span
                modified_spans.append(span)
        
        return self.exporter.export(modified_spans)

    def shutdown(self):
        """Shutdown the exporter"""
        return self.exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30000):
        """Force flush the exporter"""
        return self.exporter.force_flush(timeout_millis) 