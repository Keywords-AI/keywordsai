"""Keywords AI OpenTelemetry Exporter for Langfuse.

This module patches the OTLP exporter to send spans to Keywords AI instead of the default Langfuse endpoint.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import requests
import opentelemetry.exporter.otlp.proto.http.trace_exporter as otlp_module

logger = logging.getLogger(__name__)

# Store the original export method
_original_export = otlp_module.OTLPSpanExporter.export
_is_patched = False


def _create_patched_export(api_key: str, endpoint: str):
    """Create a patched export function with the given API key and endpoint."""
    
    def patched_export(self, spans):
        """Transform and export spans to Keywords AI."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        batch_logs = []
        
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
            if "langfuse.observation.model.name" in attributes:
                payload["model"] = attributes["langfuse.observation.model.name"]
            
            # Extract usage information
            if "langfuse.observation.usage_details" in attributes:
                try:
                    usage = json.loads(attributes["langfuse.observation.usage_details"])
                    payload["usage"] = {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }
                except Exception as e:
                    logger.warning(f"Failed to parse usage details: {e}")
            
            batch_logs.append(payload)
        
        # Send to Keywords AI
        if batch_logs:
            try:
                response = requests.post(endpoint, json=batch_logs, headers=headers, timeout=10)
                response.raise_for_status()
                logger.debug(f"Successfully exported {len(batch_logs)} spans to Keywords AI")
            except Exception as e:
                logger.warning(f"Failed to send batch to Keywords AI. Error: {e}")
        
        # Return success status
        from opentelemetry.sdk.trace.export import SpanExportResult
        return SpanExportResult.SUCCESS
    
    return patched_export


def patch_langfuse_exporter(
    api_key: Optional[str] = None,
    endpoint: str = "https://api.keywordsai.co/api/v1/traces/ingest"
):
    """
    Patch the Langfuse OpenTelemetry exporter to send spans to Keywords AI.
    
    Args:
        api_key: Keywords AI API key. If not provided, will use KEYWORDSAI_API_KEY environment variable.
        endpoint: Keywords AI traces endpoint. Defaults to production endpoint.
        
    Raises:
        ValueError: If no API key is provided and KEYWORDSAI_API_KEY is not set.
    """
    global _is_patched
    
    if _is_patched:
        logger.info("Langfuse exporter already patched for Keywords AI")
        return
    
    # Get API key from parameter or environment
    api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Keywords AI API key is required. "
            "Provide it as a parameter or set KEYWORDSAI_API_KEY environment variable."
        )
    
    # Apply the patch
    otlp_module.OTLPSpanExporter.export = _create_patched_export(api_key, endpoint)
    _is_patched = True
    logger.info(f"Langfuse exporter patched to send traces to Keywords AI at {endpoint}")


def unpatch_langfuse_exporter():
    """Restore the original Langfuse OpenTelemetry exporter."""
    global _is_patched
    
    if not _is_patched:
        logger.info("Langfuse exporter is not patched")
        return
    
    otlp_module.OTLPSpanExporter.export = _original_export
    _is_patched = False
    logger.info("Langfuse exporter restored to original behavior")


def is_patched() -> bool:
    """Check if the Langfuse exporter is currently patched."""
    return _is_patched
