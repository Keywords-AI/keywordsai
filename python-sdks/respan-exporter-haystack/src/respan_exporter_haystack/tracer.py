"""Keywords AI Tracer implementation for Haystack content tracing."""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from haystack import logging
from haystack.tracing import Span, Tracer

from .logger import RespanLogger

logger = logging.getLogger(__name__)


class RespanTracer(Tracer):
    """
    Custom tracer implementation for Keywords AI that integrates with Haystack's tracing system.
    
    This tracer captures all pipeline operations and sends them to Keywords AI for monitoring.
    It implements the Haystack Tracer protocol to seamlessly integrate with Haystack pipelines.
    """

    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Keywords AI tracer.
        
        Args:
            name: Name of the trace/pipeline
            api_key: Keywords AI API key
            base_url: Keywords AI API base URL
            metadata: Additional metadata to attach to traces
        """
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.metadata = metadata or {}
        
        # Initialize the logger for sending data
        self.kw_logger = RespanLogger(api_key=api_key, base_url=base_url)
        
        # Trace state
        self.trace_id = str(uuid.uuid4())
        self.spans: Dict[str, Dict[str, Any]] = {}
        self.completed_spans: List[Dict[str, Any]] = []  # Collect spans for batch submission
        self.trace_url: Optional[str] = None
        self.start_time = None
        self.pipeline_finished = False

    def trace(self, operation_name: str, tags: Optional[Dict[str, Any]] = None, parent_span: Optional["RespanSpan"] = None) -> "RespanSpan":
        """
        Start a new span for tracing an operation.
        
        Args:
            operation_name: Name of the operation being traced
            tags: Additional tags/metadata for the span
            parent_span: Optional parent span for nested operations
            
        Returns:
            A new RespanSpan instance
        """
        if self.start_time is None:
            self.start_time = time.time()
            
        span_id = str(uuid.uuid4())
        parent_id = parent_span.span_id if parent_span else None
        
        span = RespanSpan(
            tracer=self,
            operation_name=operation_name,
            span_id=span_id,
            trace_id=self.trace_id,
            tags=tags or {},
            parent_id=parent_id,
        )
        
        self.spans[span_id] = {
            "operation_name": operation_name,
            "span_id": span_id,
            "trace_id": self.trace_id,
            "parent_id": parent_id,
            "tags": tags or {},
            "start_time": time.time(),
            "data": {},
        }
        
        return span

    def current_span(self) -> Optional["RespanSpan"]:
        """Get the current active span."""
        # Return the most recently created span
        if self.spans:
            span_id = list(self.spans.keys())[-1]
            span_data = self.spans[span_id]
            return RespanSpan(
                tracer=self,
                operation_name=span_data["operation_name"],
                span_id=span_id,
                trace_id=self.trace_id,
                tags=span_data.get("tags", {}),
            )
        return None

    def finalize_span(
        self,
        span_id: str,
        output: Any = None,
        error: Optional[Exception] = None,
    ):
        """
        Finalize a span and collect it for batch submission.
        
        Args:
            span_id: ID of the span to finalize
            output: Output data from the operation
            error: Exception if operation failed
        """
        if span_id not in self.spans:
            return
            
        span_data = self.spans[span_id]
        end_time = time.time()
        span_data["end_time"] = end_time
        span_data["latency"] = end_time - span_data["start_time"]
        
        if output is not None:
            span_data["output"] = output
            
        if error is not None:
            span_data["error"] = str(error)
            span_data["status_code"] = 500
        else:
            span_data["status_code"] = 200
        
        # Format span for Keywords AI traces API
        try:
            formatted_span = self._format_span_for_api(span_data)
            if formatted_span is not None:  # Skip None (filtered spans)
                self.completed_spans.append(formatted_span)
            
            # If this is the root span (no parent), send the entire trace
            if span_data.get("parent_id") is None and span_data["operation_name"] == "haystack.pipeline.run":
                logger.debug(f"Root span complete - sending trace with {len(self.completed_spans)} spans")
                self.send_trace()
        except Exception as e:
            logger.warning(f"Failed to format span: {e}")

    def _format_span_for_api(self, span_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format span data for Keywords AI traces API."""
        operation_name = span_data["operation_name"]
        tags = span_data.get("tags", {})
        data = span_data.get("data", {})
        
        # Extract component info
        component_name = tags.get("haystack.component.name", "")
        component_type = tags.get("haystack.component.type", "")
        
        # Skip the tracer component itself (it's infrastructure, not business logic)
        if "RespanConnector" in component_type:
            logger.debug(f"Skipping tracer component from trace")
            return None
        
        # Convert timestamps to RFC3339 format with UTC timezone
        start_time = datetime.fromtimestamp(span_data["start_time"], tz=timezone.utc).isoformat()
        end_time = datetime.fromtimestamp(span_data["end_time"], tz=timezone.utc).isoformat()
        
        # Determine span name and log type
        if component_name:
            span_name = component_name
        else:
            span_name = self.name if operation_name == "haystack.pipeline.run" else operation_name
            
        # Determine log_type based on component type
        log_type = "workflow"  # default
        if "Generator" in component_type or "llm" in component_name.lower():
            log_type = "chat"
        elif "Builder" in component_type or "prompt" in component_name.lower():
            log_type = "task"
        elif operation_name == "haystack.pipeline.run":
            log_type = "workflow"
        else:
            log_type = "task"
        
        # Build minimal metadata (only user-provided, not Haystack internals)
        metadata = {**self.metadata}
        if component_name:
            metadata["component_name"] = component_name
        if component_type:
            metadata["component_type"] = component_type
        
        # Build the span payload for traces API
        payload = {
            "trace_unique_id": span_data["trace_id"],
            "span_unique_id": span_data["span_id"],
            "span_parent_id": span_data.get("parent_id"),
            "span_name": span_name,
            "span_workflow_name": self.name,
            "log_type": log_type,
            "start_time": start_time,
            "timestamp": end_time,
            "latency": span_data.get("latency", 0),
            "metadata": metadata,
            "disable_log": False,
        }
        
        # Extract INPUT data
        input_data = data.get("haystack.component.input") or tags.get("haystack.pipeline.input_data")
        if input_data is not None:
            payload["input"] = self._serialize_data(input_data)
        
        # Extract OUTPUT data
        output_data = data.get("haystack.component.output") or tags.get("haystack.pipeline.output_data")
        
        if output_data is not None:
            # For pipeline root span, simplify output to just the final answer
            if operation_name == "haystack.pipeline.run" and isinstance(output_data, dict):
                # Try to extract the final LLM response
                for key in ["llm", "generator", "chat"]:
                    if key in output_data and isinstance(output_data[key], dict):
                        component_output = output_data[key]
                        if "replies" in component_output:
                            replies = component_output["replies"]
                            if replies and len(replies) > 0:
                                first_reply = replies[0]
                                if hasattr(first_reply, "text"):
                                    payload["output"] = first_reply.text
                                elif hasattr(first_reply, "content"):
                                    payload["output"] = first_reply.content
                                elif isinstance(first_reply, str):
                                    payload["output"] = first_reply
                                break
                
                # If no output extracted yet, serialize but remove infrastructure keys
                if "output" not in payload:
                    cleaned_output = {k: v for k, v in output_data.items() if k != "tracer"}
                    payload["output"] = self._serialize_data(cleaned_output)
            
            # Handle different output types
            elif isinstance(output_data, dict):
                # Check for Haystack component output with replies (LLM response)
                if "replies" in output_data:
                    replies = output_data["replies"]
                    if replies and len(replies) > 0:
                        first_reply = replies[0]
                        # ChatMessage object - try .text first (new API), fallback to .content (old API)
                        if hasattr(first_reply, "text"):
                            payload["output"] = first_reply.text
                            payload["log_type"] = "chat"
                        elif hasattr(first_reply, "content"):
                            payload["output"] = first_reply.content
                            payload["log_type"] = "chat"
                        elif isinstance(first_reply, str):
                            payload["output"] = first_reply
                        else:
                            payload["output"] = str(first_reply)
                            
                # Check for LLM metadata
                if "meta" in output_data:
                    meta = output_data["meta"]
                    if isinstance(meta, list) and len(meta) > 0:
                        first_meta = meta[0]
                        model_name = first_meta.get("model", "")
                        if model_name:
                            payload["model"] = model_name
                        if "usage" in first_meta:
                            usage = first_meta["usage"]
                            prompt_tokens = usage.get("prompt_tokens", 0)
                            completion_tokens = usage.get("completion_tokens", 0)
                            payload["prompt_tokens"] = prompt_tokens
                            payload["completion_tokens"] = completion_tokens
                            
                            # Calculate cost
                            if model_name and prompt_tokens and completion_tokens:
                                cost = self._calculate_cost(model_name, prompt_tokens, completion_tokens)
                                payload["cost"] = cost
                            
                # If no specific field extracted yet, serialize entire output
                if "output" not in payload:
                    payload["output"] = self._serialize_data(output_data)
            else:
                payload["output"] = self._serialize_data(output_data)
        
        # Handle errors
        if "error" in span_data:
            payload["warnings"] = span_data["error"]
        
        # Add status code
        payload["status_code"] = span_data.get("status_code", 200)
            
        return payload
    
    def send_trace(self):
        """Send all collected spans to Keywords AI as a batch."""
        if not self.completed_spans:
            logger.debug("No spans to send")
            return
        
        if self.pipeline_finished:
            logger.debug("Trace already sent")
            return
            
        try:
            logger.debug(f"Sending trace with {len(self.completed_spans)} spans to Keywords AI")
            response = self.kw_logger.send_trace(self.completed_spans)
            
            if response:
                logger.debug(f"Trace sent successfully: {response}")
                # Extract trace info from response
                if "trace_ids" in response and response["trace_ids"]:
                    trace_id = response["trace_ids"][0]
                    self.trace_url = f"https://platform.respan.co/logs?trace_id={trace_id}"
                    
            self.pipeline_finished = True
        except Exception as e:
            logger.warning(f"Failed to send trace to Keywords AI: {e}")

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on model pricing."""
        # Pricing per 1M tokens (as of 2026)
        pricing = {
            "gpt-4o": {"prompt": 2.50, "completion": 10.00},
            "gpt-4o-mini": {"prompt": 0.150, "completion": 0.600},
            "gpt-4o-2024-11-20": {"prompt": 2.50, "completion": 10.00},
            "gpt-4o-2024-08-06": {"prompt": 2.50, "completion": 10.00},
            "gpt-4o-2024-05-13": {"prompt": 5.00, "completion": 15.00},
            "gpt-4o-mini-2024-07-18": {"prompt": 0.150, "completion": 0.600},
            "gpt-4-turbo": {"prompt": 10.00, "completion": 30.00},
            "gpt-4": {"prompt": 30.00, "completion": 60.00},
            "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
            "gpt-3.5-turbo-0125": {"prompt": 0.50, "completion": 1.50},
        }
        
        # Get pricing for model (default to gpt-3.5-turbo if not found)
        model_pricing = pricing.get(model, pricing["gpt-3.5-turbo"])
        
        # Calculate cost (pricing is per 1M tokens)
        prompt_cost = (prompt_tokens / 1_000_000) * model_pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * model_pricing["completion"]
        
        return prompt_cost + completion_cost
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data to string for logging."""
        try:
            if isinstance(data, (str, int, float, bool)):
                return str(data)
            return json.dumps(data, default=str)
        except Exception:
            return str(data)

    def get_trace_url(self) -> Optional[str]:
        """Get the URL to view this trace in Keywords AI dashboard."""
        if self.trace_url:
            return self.trace_url
        # Return a default URL pattern if not set yet
        return f"https://platform.respan.co/logs?trace_id={self.trace_id}"


class RespanSpan(Span):
    """
    Span implementation for Keywords AI tracing.
    
    Represents a single operation in the pipeline execution.
    """

    def __init__(
        self,
        tracer: RespanTracer,
        operation_name: str,
        span_id: str,
        trace_id: str,
        tags: Dict[str, Any],
        parent_id: Optional[str] = None,
    ):
        """Initialize a span."""
        self.tracer = tracer
        self.operation_name = operation_name
        self.span_id = span_id
        self.trace_id = trace_id
        self.tags = tags
        self.parent_id = parent_id
        self._is_finished = False

    def set_tag(self, key: str, value: Any) -> "RespanSpan":
        """Set a tag on the span."""
        if self.span_id in self.tracer.spans:
            if "tags" not in self.tracer.spans[self.span_id]:
                self.tracer.spans[self.span_id]["tags"] = {}
            self.tracer.spans[self.span_id]["tags"][key] = value
        return self

    def set_tags(self, tags: Dict[str, Any]) -> "RespanSpan":
        """Set multiple tags on the span."""
        for key, value in tags.items():
            self.set_tag(key, value)
        return self

    def set_content_tag(self, key: str, value: Any) -> "RespanSpan":
        """Set content data on the span."""
        if self.span_id in self.tracer.spans:
            if "data" not in self.tracer.spans[self.span_id]:
                self.tracer.spans[self.span_id]["data"] = {}
            self.tracer.spans[self.span_id]["data"][key] = value
        return self

    def raw_span(self) -> Any:
        """Get the raw span data."""
        return self.tracer.spans.get(self.span_id)

    def finish(self, output: Any = None, error: Optional[Exception] = None):
        """Finish the span and send to Keywords AI."""
        if not self._is_finished:
            self.tracer.finalize_span(self.span_id, output=output, error=error)
            self._is_finished = True

    def __enter__(self) -> "RespanSpan":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        error = exc_val if exc_type is not None else None
        self.finish(error=error)
