"""OpenTelemetry Instrumentor for Langfuse.

This module provides OTEL-compliant instrumentation for Langfuse using BaseInstrumentor.
It uses wrapt for safe, reversible monkey-patching to redirect Langfuse data to Keywords AI.

The approach: Langfuse SDK already collects spans and sends them via httpx.Client.
We simply intercept the HTTP requests and redirect them to Keywords AI with format transformation.
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
    
    This instrumentor patches Langfuse's HTTP client to intercept requests
    to the Langfuse backend and redirect them to Keywords AI instead.
    
    Usage:
        from keywordsai_instrumentation_langfuse import LangfuseInstrumentor
        
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
        """Enable instrumentation by patching Langfuse's HTTP client.
        
        This patches httpx.Client.send (which Langfuse uses) to intercept
        requests going to Langfuse backend and redirect them to Keywords AI.
        
        Args:
            api_key: Keywords AI API key (optional, uses KEYWORDSAI_API_KEY env var if not provided)
            endpoint: Keywords AI endpoint (optional, defaults to production endpoint)
        """
        self._api_key = kwargs.get("api_key") or os.getenv("KEYWORDSAI_API_KEY")
        self._endpoint = kwargs.get("endpoint") or os.getenv(
            "KEYWORDSAI_ENDPOINT",
            "https://api.keywordsai.co/api/v1/traces/ingest"
        )
        
        if not self._api_key:
            logger.warning(
                "Keywords AI API key not provided. "
                "Set KEYWORDSAI_API_KEY environment variable or pass api_key parameter."
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
    
    @staticmethod
    def _transform_langfuse_to_keywords_DEPRECATED(langfuse_batch: dict) -> list:
        """Transform Langfuse batch format to Keywords AI format.
        
        Args:
            langfuse_batch: Langfuse batch data in format:
                {
                    "batch": [
                        {
                            "type": "observation-create",
                            "body": {
                                "id": "...",
                                "traceId": "...",
                                "name": "...",
                                "type": "generation",
                                "startTime": "2024-01-01T00:00:00Z",
                                "endTime": "2024-01-01T00:00:01Z",
                                ...
                            }
                        }
                    ]
                }
            
        Returns:
            List of Keywords AI log entries in format:
                [
                    {
                        "trace_unique_id": "...",
                        "span_unique_id": "...",
                        "span_parent_id": "...",
                        "span_name": "...",
                        "span_workflow_name": "...",
                        "log_type": "generation|tool|workflow|custom",
                        "customer_identifier": "...",
                        "timestamp": "2024-01-01T00:00:01Z",
                        "start_time": "2024-01-01T00:00:00Z",
                        "latency": 1.0,
                        "input": "...",
                        "output": "...",
                        "model": "...",
                        "usage": {...}
                    }
                ]
        """
        from datetime import datetime, timezone
        
        keywords_logs = []
        
        for event in langfuse_batch.get('batch', []):
            event_type = event.get('type')
            body = event.get('body', {})
            
            # Calculate latency if we have both timestamps
            latency = None
            if 'startTime' in body and 'endTime' in body:
                try:
                    start_dt = datetime.fromisoformat(body['startTime'].replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(body['endTime'].replace('Z', '+00:00'))
                    latency = (end_dt - start_dt).total_seconds()
                except Exception:
                    pass
            
            # Build the complete Keywords AI payload
            log = {
                "trace_unique_id": body.get('traceId') or body.get('id'),
                "span_unique_id": body.get('id'),
                "span_name": body.get('name', 'unknown'),
                "log_type": LangfuseInstrumentor._map_langfuse_type(event_type, body),
            }
            
            # Add parent span ID
            if 'parentObservationId' in body:
                log['span_parent_id'] = body['parentObservationId']
            
            # Add workflow name (use trace name if available)
            if 'traceName' in body:
                log['span_workflow_name'] = body['traceName']
            else:
                log['span_workflow_name'] = body.get('name', 'unknown')
            
            # Add customer identifier
            if 'userId' in body:
                log['customer_identifier'] = body['userId']
            
            # Add timestamps
            if 'endTime' in body:
                log['timestamp'] = body['endTime']
            elif 'timestamp' in body:
                log['timestamp'] = body['timestamp']
            
            if 'startTime' in body:
                log['start_time'] = body['startTime']
            
            # Add latency
            if latency is not None:
                log['latency'] = latency
            
            # Add input (ensure it's a string)
            if 'input' in body:
                input_val = body['input']
                log['input'] = input_val if isinstance(input_val, str) else json.dumps(input_val)
            
            # Add output (ensure it's a string)
            if 'output' in body:
                output_val = body['output']
                log['output'] = output_val if isinstance(output_val, str) else json.dumps(output_val)
            
            # Add model
            if 'model' in body:
                log['model'] = body['model']
            elif 'modelName' in body:
                log['model'] = body['modelName']
            
            # Add usage information (transform to Keywords AI format)
            if 'usage' in body:
                usage = body['usage']
                if isinstance(usage, dict):
                    log['usage'] = {
                        "prompt_tokens": usage.get('promptTokens') or usage.get('prompt_tokens', 0),
                        "completion_tokens": usage.get('completionTokens') or usage.get('completion_tokens', 0),
                        "total_tokens": usage.get('totalTokens') or usage.get('total_tokens', 0)
                    }
            
            # Add metadata if present
            if 'metadata' in body:
                log['metadata'] = body['metadata']
            
            # Add level/status if present
            if 'level' in body:
                log['status'] = body['level']
            
            # Add status message if present
            if 'statusMessage' in body:
                log['error_message'] = body['statusMessage']
            
            keywords_logs.append(log)
        
        return keywords_logs
    
    @staticmethod
    def _map_langfuse_type(event_type: Optional[str], body: dict) -> str:
        """Map Langfuse event type to Keywords AI log type.
        
        Args:
            event_type: Langfuse event type
            body: Event body
            
        Returns:
            Keywords AI log type
        """
        observation_type = body.get('type', '').lower()
        
        if 'generation' in observation_type:
            return 'generation'
        elif 'span' in observation_type:
            return 'tool' if body.get('parentObservationId') else 'workflow'
        else:
            return 'custom'
