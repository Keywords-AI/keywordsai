from typing import Dict, Optional, Sequence, List, Any
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import SpanContext
from ..utils.logging import get_keywordsai_logger
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
                preview: List[Dict[str, Any]] = []
                for s in modified_spans:
                    try:
                        ctx: SpanContext = s.get_span_context()  # type: ignore[attr-defined]
                        attrs: Dict[str, Any] = getattr(s, "attributes", {}) or {}

                        def _safe(val: Any) -> Any:
                            try:
                                if isinstance(val, (bytes, bytearray)):
                                    return f"<bytes {len(val)}B>"
                                if isinstance(val, (list, tuple)):
                                    # Convert list/tuple items safely
                                    return [str(item)[:500] for item in val]
                                if isinstance(val, dict):
                                    # Convert dict values safely
                                    return {str(k): str(v)[:500] for k, v in val.items()}
                                s_val = str(val)
                                return s_val if len(s_val) <= 1000 else s_val[:1000] + "...<truncated>"
                            except Exception:
                                return "<unserializable>"

                        # Highlight likely prompt/message fields if present
                        highlighted_keys = [
                            k for k in attrs.keys()
                            if any(x in str(k).lower() for x in [
                                "prompt", "message", "messages", "input", "content",
                                "entity_input", "ai.", "openai", "request.body"
                            ])
                        ]

                        preview.append(
                            {
                                "name": getattr(s, "name", "<unknown>"),
                                "trace_id": format(ctx.trace_id, '032x') if ctx else None,
                                "span_id": format(ctx.span_id, '016x') if ctx else None,
                                "parent_span_id": getattr(s, "parent_span_id", None),
                                "kind": attrs.get("traceloop.span.kind"),
                                "entity_path": attrs.get("traceloop.entity.path"),
                                "attributes_count": len(attrs),
                                "highlighted_attributes": {
                                    str(k): _safe(attrs.get(k)) for k in highlighted_keys
                                },
                            }
                        )
                    except Exception as e:
                        preview.append({"error": f"failed_to_preview_span: {e}"})

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