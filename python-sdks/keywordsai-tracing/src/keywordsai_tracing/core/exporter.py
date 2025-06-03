from typing import Dict, Optional, Sequence
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan


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
            if base_endpoint.endswith('/api'):
                # KeywordsAI specific endpoint structure
                return f"{base_endpoint}/v1/traces"
            else:
                return f"{base_endpoint}/v1/traces"
        
        return base_endpoint
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to KeywordsAI"""
        return self.exporter.export(spans)
    
    def shutdown(self):
        """Shutdown the exporter"""
        return self.exporter.shutdown()
    
    def force_flush(self, timeout_millis: int = 30000):
        """Force flush the exporter"""
        return self.exporter.force_flush(timeout_millis) 