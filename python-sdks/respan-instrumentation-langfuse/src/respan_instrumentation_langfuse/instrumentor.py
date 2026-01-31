"""OpenTelemetry Instrumentor for Langfuse.

This module provides OTEL-compliant instrumentation for Langfuse using BaseInstrumentor.
It uses wrapt for safe, reversible monkey-patching to redirect Langfuse data to Keywords AI.

The approach: Langfuse SDK already collects OTEL spans and exports them via OTLPSpanExporter.
We simply intercept the OTLP export and redirect Langfuse spans to Keywords AI with format transformation.
"""

import logging
import os
import json
from datetime import datetime, timezone
from typing import Collection, Optional

import requests
import wrapt
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.trace.export import SpanExportResult

logger = logging.getLogger(__name__)

_instruments = ("langfuse >= 2.0.0",)


class LangfuseInstrumentor(BaseInstrumentor):
    """An instrumentor for Langfuse that redirects traces to Keywords AI.
    
    This instrumentor patches the OTLP exporter to intercept Langfuse OTEL spans
    and redirect them to Keywords AI instead.
    
    Usage:
        from respan_instrumentation_langfuse import LangfuseInstrumentor
        
        LangfuseInstrumentor().instrument(api_key="your-api-key")
        
        # Now use Langfuse normally - data goes to Keywords AI!
        from langfuse import Langfuse, observe
        
        langfuse = Langfuse()
        
        @observe()
        def my_function():
            return "traced!"
    """
    
    _api_key: Optional[str] = None
    _endpoint: Optional[str] = None
    
    def instrumentation_dependencies(self) -> Collection[str]:
        """Return the list of packages this instrumentation depends on."""
        return _instruments
    
    def _instrument(self, **kwargs):
        """Enable instrumentation by patching OTLP exporter.
        
        This patches OTLPSpanExporter.export to intercept Langfuse OTEL spans
        and redirect them to Keywords AI instead.
        
        Args:
            api_key: Keywords AI API key (optional, uses RESPAN_API_KEY env var if not provided)
            endpoint: Keywords AI endpoint (optional, defaults to production endpoint)
        """
        self._api_key = kwargs.get("api_key") or os.getenv("RESPAN_API_KEY")
        self._endpoint = kwargs.get("endpoint") or os.getenv(
            "RESPAN_ENDPOINT",
            "https://api.respan.ai/api/v1/traces/ingest"
        )
        
        if not self._api_key:
            logger.warning(
                "Keywords AI API key not provided. "
                "Set RESPAN_API_KEY environment variable or pass api_key parameter."
            )
            return
        
        # Patch OTLP exporter to intercept Langfuse spans
        self._patch_otlp_exporter()
        
        logger.info("Langfuse instrumentation enabled for Keywords AI")
    
    def _uninstrument(self, **kwargs):
        """Disable instrumentation by removing patches."""
        # wrapt handles unwrapping automatically if we stored the wrapper
        logger.info("Langfuse instrumentation disabled")
    
    def _patch_otlp_exporter(self):
        """Patch OTLPSpanExporter to intercept Langfuse spans.
        
        This uses wrapt to safely wrap the export method so we can
        intercept OTEL spans going to Langfuse and redirect to Keywords AI.
        
        IMPORTANT: We only intercept exports going to Langfuse URLs to avoid
        breaking other OTLP exports the user might have configured.
        """
        api_key = self._api_key
        endpoint = self._endpoint
        
        def export_wrapper(wrapped, instance, args, kwargs):
            """Wrapper for OTLPSpanExporter.export that intercepts Langfuse spans."""
            # Check if this exporter is sending to Langfuse
            exporter_endpoint = getattr(instance, '_endpoint', '')
            
            is_langfuse_exporter = (
                'langfuse' in exporter_endpoint.lower() or
                '/api/public/otel' in exporter_endpoint or
                'cloud.langfuse.com' in exporter_endpoint
            )
            
            # If NOT sending to Langfuse, pass through to original export
            if not is_langfuse_exporter:
                logger.debug(f"Passing through non-Langfuse export to: {exporter_endpoint}")
                return wrapped(*args, **kwargs)
            
            # This is a Langfuse export - intercept and redirect
            logger.debug(f"Intercepting Langfuse OTLP export from: {exporter_endpoint}")
            
            # Get the spans (first positional arg)
            spans = args[0] if args else kwargs.get('spans', [])
            
            try:
                # Transform OTEL spans to Keywords AI format
                keywords_logs = []
                
                for span in spans:
                    attributes = dict(span.attributes) if span.attributes else {}
                    
                    # Map Langfuse observation types to Keywords AI log types
                    langfuse_type = attributes.get("langfuse.observation.type", "span")
                    log_type_mapping = {
                        "span": "workflow" if not span.parent else "tool",
                        "generation": "generation"
                    }
                    log_type = log_type_mapping.get(langfuse_type, "custom")
                    
                    # Convert timestamps
                    start_time_ns = span.start_time
                    end_time_ns = span.end_time
                    start_time_iso = datetime.fromtimestamp(start_time_ns / 1e9, tz=timezone.utc).isoformat()
                    timestamp_iso = datetime.fromtimestamp(end_time_ns / 1e9, tz=timezone.utc).isoformat()
                    latency = (end_time_ns - start_time_ns) / 1e9
                    
                    # Build the payload
                    payload = {
                        "trace_unique_id": format(span.context.trace_id, '032x'),
                        "span_unique_id": format(span.context.span_id, '016x'),
                        "span_parent_id": format(span.parent.span_id, '016x') if span.parent else None,
                        "span_name": span.name,
                        "span_workflow_name": attributes.get("langfuse.trace.name", span.name),
                        "log_type": log_type,
                        "customer_identifier": attributes.get("user.id"),
                        "timestamp": timestamp_iso,
                        "start_time": start_time_iso,
                        "latency": latency,
                    }
                    
                    # Extract input
                    if "langfuse.observation.input" in attributes:
                        input_str = attributes["langfuse.observation.input"]
                        payload["input"] = input_str if isinstance(input_str, str) else json.dumps(input_str)
                    
                    # Extract output
                    if "langfuse.observation.output" in attributes:
                        output_str = attributes["langfuse.observation.output"]
                        payload["output"] = output_str if isinstance(output_str, str) else json.dumps(output_str)
                    
                    # Extract model
                    if "langfuse.observation.model" in attributes:
                        payload["model"] = attributes["langfuse.observation.model"]
                    
                    # Extract usage information
                    if "langfuse.usage.input" in attributes:
                        payload.setdefault("usage", {})["prompt_tokens"] = attributes["langfuse.usage.input"]
                    if "langfuse.usage.output" in attributes:
                        payload.setdefault("usage", {})["completion_tokens"] = attributes["langfuse.usage.output"]
                    if "langfuse.usage.total" in attributes:
                        payload.setdefault("usage", {})["total_tokens"] = attributes["langfuse.usage.total"]
                    
                    # Extract metadata
                    metadata = {}
                    for key, value in attributes.items():
                        if key.startswith("langfuse.metadata."):
                            metadata_key = key.replace("langfuse.metadata.", "")
                            metadata[metadata_key] = value
                    if metadata:
                        payload["metadata"] = metadata
                    
                    keywords_logs.append(payload)
                
                logger.debug(f"Transformed {len(keywords_logs)} OTEL spans to Keywords AI format")
                
                # Send to Keywords AI
                if keywords_logs:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                    response = requests.post(endpoint, json=keywords_logs, headers=headers, timeout=10)
                    response.raise_for_status()
                    logger.debug(f"Successfully sent {len(keywords_logs)} spans to Keywords AI")
                
                # Return success to Langfuse
                return SpanExportResult.SUCCESS
                
            except Exception as e:
                logger.error(f"Failed to intercept and transform Langfuse spans: {e}", exc_info=True)
                # Return failure
                return SpanExportResult.FAILURE
        
        # Use wrapt to patch OTLPSpanExporter.export
        wrapt.wrap_function_wrapper(
            module="opentelemetry.exporter.otlp.proto.http.trace_exporter",
            name="OTLPSpanExporter.export",
            wrapper=export_wrapper
        )
        
        logger.debug("Patched OTLPSpanExporter.export to intercept Langfuse requests")

