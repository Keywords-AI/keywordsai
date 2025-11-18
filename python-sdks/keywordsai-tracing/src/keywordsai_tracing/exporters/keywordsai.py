from typing import Dict, Optional, Sequence, List, Any
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import SpanContext
from ..utils.logging import get_keywordsai_logger, build_spans_export_preview
from ..utils.preprocessing.span_processing import should_make_root_span

logger = get_keywordsai_logger('core.exporter')


class ModifiedSpan:
    """A proxy wrapper that forwards all attributes to the original span except parent_span_id"""
    
    def __init__(self, original_span: ReadableSpan):
        self._original_span = original_span
    
    def __getattr__(self, name):
        """Forward all attribute access to the original span"""
        if name == 'parent_span_id':
            return None  # Override parent_span_id to None
        return getattr(self._original_span, name)


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
        # Debug: print a sanitized preview of what will be exported
        try:
            if logger.isEnabledFor(10):  # logging.DEBUG
                preview = build_spans_export_preview(modified_spans)
                logger.debug("[KeywordsAI Debug] Export preview (sanitized): %s", preview)
        except Exception:
            # Never fail export due to debug logging issues
            pass

        return self.exporter.export(modified_spans)

    def shutdown(self):
        """Shutdown the exporter"""
        return self.exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30000):
        """Force flush the exporter"""
        return self.exporter.force_flush(timeout_millis) 