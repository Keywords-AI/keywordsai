"""Keywords AI LiteLLM Integration.

This module provides instrumentation for LiteLLM to send traces to Keywords AI.

Two integration methods are provided:

1. LiteLLMInstrumentor (Recommended)
   - OpenTelemetry-compliant automatic instrumentation
   - Uses wrapt for safe, reversible monkey-patching
   - Automatically captures all LiteLLM calls

2. KeywordsAILiteLLMCallback
   - LiteLLM-native callback class
   - Manual trace hierarchy via keywordsai_params

Example - Instrumentor:
    from keywordsai_exporter_litellm import LiteLLMInstrumentor
    import litellm

    LiteLLMInstrumentor().instrument(api_key="your-api-key")
    response = litellm.completion(model="gpt-4", messages=[...])

Example - Callback:
    from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback
    import litellm

    callback = KeywordsAILiteLLMCallback(api_key="your-api-key")
    litellm.success_callback = [callback.log_success_event]
    litellm.failure_callback = [callback.log_failure_event]
    response = litellm.completion(model="gpt-4", messages=[...])
"""

import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Collection, Dict, List, Optional, Union

import litellm
import requests
import wrapt
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter, SpanExportResult

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

_instruments = ("litellm >= 1.0.0",)
DEFAULT_KEYWORDSAI_ENDPOINT = "https://api.keywordsai.co/api/v1/traces/ingest"


# =============================================================================
# Span Exporter (OTEL)
# =============================================================================

class KeywordsAISpanExporter(SpanExporter):
    """Custom OTEL SpanExporter that sends spans to Keywords AI endpoint.
    
    This exporter transforms OTEL spans into the Keywords AI trace format
    and sends them via HTTP POST to the Keywords AI API.
    
    The payload format matches the Keywords AI traces/ingest endpoint:
    {
        "trace_unique_id": "...",
        "span_unique_id": "...",
        "span_parent_id": "...",
        "span_name": "...",
        "span_workflow_name": "...",
        "log_type": "generation|workflow|tool|custom",
        "timestamp": "...",
        "start_time": "...",
        "latency": 1.0,
        "input": "...",
        "output": "...",
        "model": "...",
        "usage": {...},
        "customer_identifier": "...",
        "metadata": {...}
    }
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 10,
    ):
        self.api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        self.endpoint = endpoint or os.getenv(
            "KEYWORDSAI_ENDPOINT",
            DEFAULT_KEYWORDSAI_ENDPOINT
        )
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning(
                "Keywords AI API key not provided. "
                "Set KEYWORDSAI_API_KEY environment variable or pass api_key parameter."
            )
    
    def export(self, spans) -> SpanExportResult:
        """Export spans to Keywords AI endpoint as a batch."""
        if not self.api_key:
            return SpanExportResult.FAILURE
        
        try:
            # Transform all spans to Keywords AI format
            keywords_logs = []
            for span in spans:
                logger.debug(f"Processing span: {span.name}, trace_id={format(span.context.trace_id, '032x')}, parent={span.parent}")
                payload = self._transform_span_to_payload(span)
                if payload:
                    keywords_logs.append(payload)
                    logger.debug(f"Added payload for span: {payload.get('span_name')}, log_type={payload.get('log_type')}")
            
            # Send as batch if we have any logs
            if keywords_logs:
                for p in keywords_logs:
                    logger.info(f"Sending span: name={p.get('span_name')}, trace_id={p.get('trace_unique_id')}, span_id={p.get('span_unique_id')}, parent_id={p.get('span_parent_id')}, log_type={p.get('log_type')}")
                self._send_batch_to_keywordsai(keywords_logs)
                logger.debug(f"Successfully sent {len(keywords_logs)} spans to Keywords AI")
            
            return SpanExportResult.SUCCESS
        except Exception as e:
            logger.error(f"Failed to export spans to Keywords AI: {e}", exc_info=True)
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        pass
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any pending spans."""
        return True
    
    def _transform_span_to_payload(self, span) -> Optional[Dict[str, Any]]:
        """Transform an OTEL span to Keywords AI trace payload format."""
        attributes = dict(span.attributes) if span.attributes else {}
        
        # Extract timestamps
        start_time_ns = span.start_time
        end_time_ns = span.end_time
        start_time_iso = datetime.fromtimestamp(start_time_ns / 1e9, tz=timezone.utc).isoformat()
        timestamp_iso = datetime.fromtimestamp(end_time_ns / 1e9, tz=timezone.utc).isoformat()
        latency = (end_time_ns - start_time_ns) / 1e9
        
        # Determine log_type based on span name and attributes
        is_llm_span = span.name.startswith("litellm")
        has_parent = span.parent is not None
        
        if is_llm_span:
            log_type = "generation"
        elif has_parent:
            log_type = "tool"
        else:
            log_type = "workflow"
        
        # Build the payload matching Keywords AI trace format
        payload = {
            "trace_unique_id": format(span.context.trace_id, '032x'),
            "span_unique_id": format(span.context.span_id, '016x'),
            "span_name": span.name,
            "span_workflow_name": attributes.get("workflow.name", span.name),
            "log_type": log_type,
            "timestamp": timestamp_iso,
            "start_time": start_time_iso,
            "latency": latency,
        }
        
        # Add parent span if exists
        if span.parent:
            payload["span_parent_id"] = format(span.parent.span_id, '016x')
        
        # Add model
        model = attributes.get("litellm.model") or attributes.get("llm.model")
        if model:
            payload["model"] = model
        
        # Add input (messages as JSON string)
        if "litellm.messages" in attributes:
            messages = attributes["litellm.messages"]
            payload["input"] = messages if isinstance(messages, str) else json.dumps(messages)
        
        # Add output (completion as JSON string)
        if "litellm.completion" in attributes:
            completion = attributes["litellm.completion"]
            payload["output"] = completion if isinstance(completion, str) else json.dumps(completion)
        
        # Add usage info as nested object
        usage = {}
        if "litellm.prompt_tokens" in attributes:
            usage["prompt_tokens"] = attributes["litellm.prompt_tokens"]
        if "litellm.completion_tokens" in attributes:
            usage["completion_tokens"] = attributes["litellm.completion_tokens"]
        if "litellm.total_tokens" in attributes:
            usage["total_tokens"] = attributes["litellm.total_tokens"]
        if usage:
            payload["usage"] = usage
        
        # Add error info
        if attributes.get("error"):
            payload["error_message"] = attributes.get("exception.message", str(attributes.get("error")))
            payload["status"] = "error"
        
        # Add stream flag
        if "litellm.stream" in attributes:
            payload["stream"] = attributes["litellm.stream"]
        
        # Add tools if present
        if "litellm.tools" in attributes:
            tools = attributes["litellm.tools"]
            if isinstance(tools, str):
                try:
                    tools = json.loads(tools)
                except json.JSONDecodeError:
                    pass
            payload["tools"] = tools
        
        if "litellm.tool_choice" in attributes:
            tool_choice = attributes["litellm.tool_choice"]
            if isinstance(tool_choice, str):
                try:
                    tool_choice = json.loads(tool_choice)
                except json.JSONDecodeError:
                    pass
            payload["tool_choice"] = tool_choice
        
        # Extract customer_identifier and metadata from keywordsai params
        metadata = {}
        for key, value in attributes.items():
            if key.startswith("keywordsai."):
                param_key = key.replace("keywordsai.", "")
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                
                # Special handling for known top-level fields
                if param_key == "customer_identifier":
                    payload["customer_identifier"] = value
                elif param_key == "customer_params":
                    if isinstance(value, dict):
                        payload["customer_identifier"] = value.get("customer_identifier")
                        # Add other customer params to metadata
                        for k, v in value.items():
                            if k != "customer_identifier":
                                metadata[f"customer_{k}"] = v
                elif param_key == "thread_identifier":
                    payload["thread_identifier"] = value
                elif param_key == "metadata":
                    if isinstance(value, dict):
                        metadata.update(value)
                else:
                    metadata[param_key] = value
        
        if metadata:
            payload["metadata"] = metadata
        
        return payload
    
    def _send_batch_to_keywordsai(self, payloads: List[Dict[str, Any]]) -> None:
        """Send batch of payloads to Keywords AI endpoint."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Send as a list (batch)
        logger.debug(f"POST to {self.endpoint} with {len(payloads)} payloads")
        response = requests.post(
            self.endpoint,
            json=payloads,
            headers=headers,
            timeout=self.timeout,
        )
        
        logger.info(f"Keywords AI API response: status={response.status_code}, body={response.text[:200] if response.text else 'empty'}")
        
        if response.status_code != 200:
            logger.warning(
                f"Keywords AI API returned {response.status_code}: {response.text}"
            )
            response.raise_for_status()


# =============================================================================
# LiteLLM Callback
# =============================================================================

class KeywordsAILiteLLMCallback:
    """LiteLLM-compatible callback class that sends logs to Keywords AI.
    
    This class implements the interface expected by LiteLLM's callback system,
    allowing it to be used with `litellm.success_callback`.
    
    The payload format matches the Keywords AI traces/ingest endpoint.
    
    Note: LiteLLM's success_callback and failure_callback expect callable functions,
    not class instances. Pass the bound methods directly.
    
    Usage:
        import litellm
        from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback
        
        callback = KeywordsAILiteLLMCallback(api_key="your-api-key")
        # Pass the bound methods to success_callback and failure_callback
        litellm.success_callback = [callback.log_success_event]
        litellm.failure_callback = [callback.log_failure_event]
        
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 10,
    ):
        self.api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        self.endpoint = endpoint or os.getenv(
            "KEYWORDSAI_ENDPOINT",
            DEFAULT_KEYWORDSAI_ENDPOINT
        )
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning(
                "Keywords AI API key not provided. "
                "Set KEYWORDSAI_API_KEY environment variable or pass api_key parameter."
            )
    
    def log_success_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Log successful LLM completion to Keywords AI.
        
        This method is called by LiteLLM when a completion succeeds.
        """
        self._log_event(kwargs, response_obj, start_time, end_time, error=None)
    
    async def async_log_success_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Async version of log_success_event."""
        # Run in thread to avoid blocking async context
        thread = threading.Thread(
            target=self._log_event,
            args=(kwargs, response_obj, start_time, end_time, None),
        )
        thread.start()
    
    def log_failure_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Log failed LLM completion to Keywords AI.
        
        This method is called by LiteLLM when a completion fails.
        """
        error = kwargs.get("exception") or kwargs.get("traceback_exception")
        self._log_event(kwargs, response_obj, start_time, end_time, error=error)
    
    async def async_log_failure_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Async version of log_failure_event."""
        error = kwargs.get("exception") or kwargs.get("traceback_exception")
        # Run in thread to avoid blocking async context
        thread = threading.Thread(
            target=self._log_event,
            args=(kwargs, response_obj, start_time, end_time, error),
        )
        thread.start()
    
    def _log_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: datetime,
        end_time: datetime,
        error: Optional[Exception],
    ) -> None:
        """Internal method to log event to Keywords AI."""
        if not self.api_key:
            logger.warning("Keywords AI API key not set, skipping log")
            return
        
        try:
            # Extract model and messages
            model = kwargs.get("model") or kwargs.get("litellm_params", {}).get("model")
            messages = kwargs.get("messages", [])
            
            # Get metadata from litellm_params
            litellm_params = kwargs.get("litellm_params", {})
            metadata = litellm_params.get("metadata", {}) or {}
            keywordsai_params = metadata.get("keywordsai_params", {})
            
            # Calculate latency
            latency = (end_time - start_time).total_seconds()
            
            # Get trace and span IDs from metadata, or generate new ones
            # This allows users to group calls into the same trace by passing trace_id
            trace_id = keywordsai_params.get("trace_id") or uuid.uuid4().hex
            span_id = keywordsai_params.get("span_id") or uuid.uuid4().hex[:16]
            parent_span_id = keywordsai_params.get("parent_span_id")
            
            # Format timestamps with timezone (convert to UTC)
            if hasattr(start_time, 'isoformat'):
                # Convert to UTC if no timezone, otherwise convert to UTC
                if start_time.tzinfo is None:
                    # Assume local time, convert to UTC
                    start_time = start_time.astimezone(timezone.utc)
                else:
                    start_time = start_time.astimezone(timezone.utc)
                start_time_iso = start_time.isoformat()
            else:
                start_time_iso = str(start_time)
            
            if hasattr(end_time, 'isoformat'):
                # Convert to UTC if no timezone, otherwise convert to UTC
                if end_time.tzinfo is None:
                    # Assume local time, convert to UTC
                    end_time = end_time.astimezone(timezone.utc)
                else:
                    end_time = end_time.astimezone(timezone.utc)
                end_time_iso = end_time.isoformat()
            else:
                end_time_iso = str(end_time)
            
            # Build payload matching Keywords AI trace format
            payload = {
                "trace_unique_id": trace_id,
                "span_unique_id": span_id,
                "span_name": keywordsai_params.get("span_name", "litellm.completion"),
                "span_workflow_name": keywordsai_params.get("workflow_name", "litellm"),
                "log_type": "generation",
                "timestamp": end_time_iso,
                "start_time": start_time_iso,
                "latency": latency,
                "model": model,
                "input": json.dumps(messages),
                "stream": kwargs.get("stream", False),
            }
            
            # Add parent span ID if provided (for trace hierarchy)
            if parent_span_id:
                payload["span_parent_id"] = parent_span_id
            
            # Add tools if present
            if kwargs.get("tools"):
                payload["tools"] = kwargs["tools"]
            if kwargs.get("tool_choice"):
                payload["tool_choice"] = kwargs["tool_choice"]
            
            # Handle success vs failure
            if error:
                payload["status"] = "error"
                payload["error_message"] = str(error)
            else:
                payload["status"] = "success"
                # Extract response data
                if response_obj:
                    if hasattr(response_obj, "model_dump"):
                        response_dict = response_obj.model_dump(mode="json")
                    elif hasattr(response_obj, "dict"):
                        response_dict = response_obj.dict()
                    elif isinstance(response_obj, dict):
                        response_dict = response_obj
                    else:
                        response_dict = {}
                    
                    # Extract completion message as output
                    choices = response_dict.get("choices", [])
                    if choices:
                        message = choices[0].get("message", {})
                        payload["output"] = json.dumps(message)
                    
                    # Extract usage
                    usage = response_dict.get("usage", {})
                    if usage:
                        payload["usage"] = {
                            "prompt_tokens": usage.get("prompt_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "total_tokens": usage.get("total_tokens"),
                        }
            
            # Extract customer_identifier and metadata from keywordsai_params
            extra_metadata = {}
            
            if "customer_identifier" in keywordsai_params:
                payload["customer_identifier"] = keywordsai_params["customer_identifier"]
            
            if "customer_params" in keywordsai_params:
                customer_params = keywordsai_params["customer_params"]
                if isinstance(customer_params, dict):
                    payload["customer_identifier"] = customer_params.get("customer_identifier")
                    for k, v in customer_params.items():
                        if k != "customer_identifier":
                            extra_metadata[f"customer_{k}"] = v
            
            if "thread_identifier" in keywordsai_params:
                payload["thread_identifier"] = keywordsai_params["thread_identifier"]
            
            if "metadata" in keywordsai_params:
                if isinstance(keywordsai_params["metadata"], dict):
                    extra_metadata.update(keywordsai_params["metadata"])
            
            # Add other keywordsai params to metadata (excluding trace/span IDs)
            excluded_keys = ("customer_identifier", "customer_params", "thread_identifier", 
                           "metadata", "workflow_name", "trace_id", "span_id", "parent_span_id", "span_name")
            for key, value in keywordsai_params.items():
                if key not in excluded_keys:
                    extra_metadata[key] = value
            
            if extra_metadata:
                payload["metadata"] = extra_metadata
            
            # Log the payload being sent
            logger.info(f"Callback sending span: name={payload.get('span_name')}, trace_id={payload.get('trace_unique_id')}, span_id={payload.get('span_unique_id')}, parent_id={payload.get('span_parent_id')}, thread_id={payload.get('thread_identifier')}, has_input={bool(payload.get('input'))}, has_output={bool(payload.get('output'))}")
            logger.debug(f"Full callback payload: {json.dumps(payload, indent=2, default=str)}")
            
            # Send to Keywords AI as a batch (list with single item)
            self._send_payload([payload])
            
        except Exception as e:
            logger.error(f"Keywords AI logging error: {e}", exc_info=True)
    
    def send_workflow_span(
        self,
        trace_id: str,
        span_id: str,
        workflow_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        parent_span_id: Optional[str] = None,
        customer_identifier: Optional[str] = None,
        thread_identifier: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        input_data: Optional[Any] = None,
        output_data: Optional[Any] = None,
    ) -> None:
        """Send a workflow/parent span to Keywords AI.
        
        This should be called to create a parent span before making LLM calls
        that will be grouped under this workflow. Call with start_time at the
        beginning, then call again with end_time when the workflow completes.
        
        Args:
            trace_id: Unique trace identifier (same for all spans in the trace)
            span_id: Unique span identifier for this workflow span
            workflow_name: Name of the workflow
            start_time: Start time of the workflow
            end_time: End time of the workflow (set when workflow completes)
            parent_span_id: Parent span ID if this is a nested workflow
            customer_identifier: Customer identifier for the trace
            thread_identifier: Thread identifier for grouping
            metadata: Additional metadata
        
        Example:
            callback = KeywordsAILiteLLMCallback(api_key="...")
            
            # Create workflow span
            trace_id = uuid.uuid4().hex
            workflow_span_id = uuid.uuid4().hex[:16]
            start = datetime.now(timezone.utc)
            
            # Make LLM calls with parent_span_id referencing workflow_span_id
            response = litellm.completion(
                model="gpt-4",
                messages=[...],
                metadata={"keywordsai_params": {
                    "trace_id": trace_id,
                    "parent_span_id": workflow_span_id,
                }}
            )
            
            # Send workflow span when done
            callback.send_workflow_span(
                trace_id=trace_id,
                span_id=workflow_span_id,
                workflow_name="my_workflow",
                start_time=start,
                end_time=datetime.now(timezone.utc),
            )
        """
        if not self.api_key:
            logger.warning("Keywords AI API key not set, skipping workflow span")
            return
        
        try:
            now = datetime.now(timezone.utc)
            start = start_time or now
            end = end_time or now
            
            start_time_iso = start.isoformat() if hasattr(start, 'isoformat') else str(start)
            end_time_iso = end.isoformat() if hasattr(end, 'isoformat') else str(end)
            latency = (end - start).total_seconds() if end_time else 0.0
            
            payload = {
                "trace_unique_id": trace_id,
                "span_unique_id": span_id,
                "span_name": workflow_name,
                "span_workflow_name": workflow_name,
                "log_type": "workflow",
                "timestamp": end_time_iso,
                "start_time": start_time_iso,
                "latency": latency,
                "status": "success",
            }
            
            if parent_span_id:
                payload["span_parent_id"] = parent_span_id
            
            if customer_identifier:
                payload["customer_identifier"] = customer_identifier
            
            if thread_identifier:
                payload["thread_identifier"] = thread_identifier
            
            if metadata:
                payload["metadata"] = metadata
            
            if input_data:
                payload["input"] = input_data if isinstance(input_data, str) else json.dumps(input_data)
            
            if output_data:
                payload["output"] = output_data if isinstance(output_data, str) else json.dumps(output_data)
            
            logger.info(f"Callback sending workflow span: name={workflow_name}, trace_id={trace_id}, span_id={span_id}, parent_id={parent_span_id}")
            logger.debug(f"Full workflow span payload: {json.dumps(payload, indent=2, default=str)}")
            self._send_payload([payload])
            
        except Exception as e:
            logger.error(f"Keywords AI workflow span error: {e}", exc_info=True)
    
    def _send_payload(self, payloads: List[Dict[str, Any]]) -> None:
        """Send payload to Keywords AI endpoint."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            
            response = requests.post(
                url=self.endpoint,
                headers=headers,
                json=payloads,  # Send as list (batch)
                timeout=self.timeout,
            )
            
            logger.info(f"Callback API response: status={response.status_code}, body={response.text[:200] if response.text else 'empty'}")
            
            if response.status_code == 200:
                logger.debug("Keywords AI Logging - Success!")
            else:
                logger.warning(
                    f"Keywords AI Logging - Error: {response.status_code}, {response.text}"
                )
        except Exception as e:
            logger.error(f"Keywords AI request error: {e}")


# =============================================================================
# OTEL Instrumentor
# =============================================================================

class LiteLLMInstrumentor(BaseInstrumentor):
    """OpenTelemetry instrumentor for LiteLLM that exports traces to Keywords AI.
    
    This instrumentor uses wrapt to patch LiteLLM's completion functions
    and captures spans with LLM-specific attributes, then exports them
    to the Keywords AI platform.
    
    Usage:
        from keywordsai_exporter_litellm import LiteLLMInstrumentor
        
        # Instrument LiteLLM
        LiteLLMInstrumentor().instrument(api_key="your-api-key")
        
        # Now use LiteLLM normally - data goes to Keywords AI!
        import litellm
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    _api_key: Optional[str] = None
    _endpoint: Optional[str] = None
    _tracer_provider: Optional[TracerProvider] = None
    _tracer: Optional[trace.Tracer] = None
    _exporter: Optional[KeywordsAISpanExporter] = None
    
    def instrumentation_dependencies(self) -> Collection[str]:
        """Return the list of packages this instrumentation depends on."""
        return _instruments
    
    def _instrument(self, **kwargs):
        """Enable instrumentation by patching LiteLLM functions.
        
        This patches litellm.completion and litellm.acompletion to create
        OTEL spans and export them to Keywords AI.
        
        Args:
            api_key: Keywords AI API key (optional, uses KEYWORDSAI_API_KEY env var)
            endpoint: Keywords AI endpoint (optional, defaults to production endpoint)
            tracer_provider: Custom TracerProvider (optional)
        """
        self._api_key = kwargs.get("api_key") or os.getenv("KEYWORDSAI_API_KEY")
        self._endpoint = kwargs.get("endpoint") or os.getenv(
            "KEYWORDSAI_ENDPOINT",
            DEFAULT_KEYWORDSAI_ENDPOINT
        )
        
        if not self._api_key:
            logger.warning(
                "Keywords AI API key not provided. "
                "Set KEYWORDSAI_API_KEY environment variable or pass api_key parameter."
            )
            return
        
        # Setup tracer provider if not provided
        tracer_provider = kwargs.get("tracer_provider")
        if tracer_provider is None:
            # Create custom exporter
            self._exporter = KeywordsAISpanExporter(
                api_key=self._api_key,
                endpoint=self._endpoint,
            )
            
            # Create tracer provider with Keywords AI exporter
            # Use SimpleSpanProcessor for immediate export (better for debugging)
            # or BatchSpanProcessor for production (better performance)
            resource = Resource.create({
                "service.name": kwargs.get("service_name", "litellm-service"),
            })
            self._tracer_provider = TracerProvider(resource=resource)
            
            # Use SimpleSpanProcessor for immediate export
            self._tracer_provider.add_span_processor(SimpleSpanProcessor(self._exporter))
            trace.set_tracer_provider(self._tracer_provider)
        else:
            self._tracer_provider = tracer_provider
            self._exporter = None
        
        self._tracer = trace.get_tracer(__name__)
        
        # Patch LiteLLM functions using wrapt
        self._patch_litellm()
        
        logger.info("LiteLLM instrumentation enabled for Keywords AI")
    
    def _uninstrument(self, **kwargs):
        """Disable instrumentation by removing patches."""
        self._unpatch_litellm()
        
        # Force flush and shutdown tracer provider
        if self._tracer_provider:
            # Force flush to ensure all spans are exported
            self._tracer_provider.force_flush()
            self._tracer_provider.shutdown()
            self._tracer_provider = None
        
        self._tracer = None
        self._exporter = None
        logger.info("LiteLLM instrumentation disabled")
    
    def flush(self):
        """Force flush all pending spans to Keywords AI."""
        if self._tracer_provider:
            self._tracer_provider.force_flush()
            logger.debug("Forced flush of all pending spans")
    
    def _patch_litellm(self):
        """Patch LiteLLM's completion functions using wrapt."""
        tracer = self._tracer
        api_key = self._api_key
        endpoint = self._endpoint
        
        def completion_wrapper(wrapped, instance, args, kwargs):
            """Wrapper for litellm.completion that creates OTEL spans."""
            model = kwargs.get("model") or (args[0] if args else "unknown")
            messages = kwargs.get("messages", [])
            stream = kwargs.get("stream", False)
            
            with tracer.start_as_current_span(
                "litellm.completion",
                kind=trace.SpanKind.CLIENT,
            ) as span:
                # Set span attributes
                span.set_attribute("litellm.model", model)
                span.set_attribute("litellm.stream", stream)
                span.set_attribute("litellm.messages", json.dumps(messages))
                
                if kwargs.get("tools"):
                    span.set_attribute("litellm.tools", json.dumps(kwargs["tools"]))
                if kwargs.get("tool_choice"):
                    tool_choice = kwargs["tool_choice"]
                    if isinstance(tool_choice, dict):
                        span.set_attribute("litellm.tool_choice", json.dumps(tool_choice))
                    else:
                        span.set_attribute("litellm.tool_choice", str(tool_choice))
                
                # Extract and set keywordsai params from metadata
                metadata = kwargs.get("metadata", {}) or {}
                keywordsai_params = metadata.get("keywordsai_params", {})
                for key, value in keywordsai_params.items():
                    if isinstance(value, (dict, list)):
                        span.set_attribute(f"keywordsai.{key}", json.dumps(value))
                    else:
                        span.set_attribute(f"keywordsai.{key}", value)
                
                try:
                    result = wrapped(*args, **kwargs)
                    
                    # Handle streaming responses
                    if stream:
                        # For streaming, we wrap the iterator
                        return _wrap_streaming_response(result, span, api_key, endpoint)
                    
                    # Handle non-streaming response
                    if hasattr(result, "model_dump"):
                        result_dict = result.model_dump(mode="json")
                    elif hasattr(result, "dict"):
                        result_dict = result.dict()
                    elif isinstance(result, dict):
                        result_dict = result
                    else:
                        result_dict = {}
                    
                    # Set response attributes
                    choices = result_dict.get("choices", [])
                    if choices:
                        completion = choices[0].get("message", {})
                        span.set_attribute("litellm.completion", json.dumps(completion))
                    
                    usage = result_dict.get("usage", {})
                    if usage:
                        span.set_attribute("litellm.prompt_tokens", usage.get("prompt_tokens", 0))
                        span.set_attribute("litellm.completion_tokens", usage.get("completion_tokens", 0))
                        span.set_attribute("litellm.total_tokens", usage.get("total_tokens", 0))
                    
                    return result
                    
                except Exception as e:
                    span.set_attribute("error", True)
                    span.set_attribute("exception.type", type(e).__name__)
                    span.set_attribute("exception.message", str(e))
                    raise
        
        async def acompletion_wrapper(wrapped, instance, args, kwargs):
            """Wrapper for litellm.acompletion that creates OTEL spans."""
            model = kwargs.get("model") or (args[0] if args else "unknown")
            messages = kwargs.get("messages", [])
            stream = kwargs.get("stream", False)
            
            with tracer.start_as_current_span(
                "litellm.acompletion",
                kind=trace.SpanKind.CLIENT,
            ) as span:
                # Set span attributes
                span.set_attribute("litellm.model", model)
                span.set_attribute("litellm.stream", stream)
                span.set_attribute("litellm.messages", json.dumps(messages))
                
                if kwargs.get("tools"):
                    span.set_attribute("litellm.tools", json.dumps(kwargs["tools"]))
                if kwargs.get("tool_choice"):
                    tool_choice = kwargs["tool_choice"]
                    if isinstance(tool_choice, dict):
                        span.set_attribute("litellm.tool_choice", json.dumps(tool_choice))
                    else:
                        span.set_attribute("litellm.tool_choice", str(tool_choice))
                
                # Extract and set keywordsai params from metadata
                metadata = kwargs.get("metadata", {}) or {}
                keywordsai_params = metadata.get("keywordsai_params", {})
                for key, value in keywordsai_params.items():
                    if isinstance(value, (dict, list)):
                        span.set_attribute(f"keywordsai.{key}", json.dumps(value))
                    else:
                        span.set_attribute(f"keywordsai.{key}", value)
                
                try:
                    result = await wrapped(*args, **kwargs)
                    
                    # Handle streaming responses
                    if stream:
                        return _wrap_async_streaming_response(result, span, api_key, endpoint)
                    
                    # Handle non-streaming response
                    if hasattr(result, "model_dump"):
                        result_dict = result.model_dump(mode="json")
                    elif hasattr(result, "dict"):
                        result_dict = result.dict()
                    elif isinstance(result, dict):
                        result_dict = result
                    else:
                        result_dict = {}
                    
                    # Set response attributes
                    choices = result_dict.get("choices", [])
                    if choices:
                        completion = choices[0].get("message", {})
                        span.set_attribute("litellm.completion", json.dumps(completion))
                    
                    usage = result_dict.get("usage", {})
                    if usage:
                        span.set_attribute("litellm.prompt_tokens", usage.get("prompt_tokens", 0))
                        span.set_attribute("litellm.completion_tokens", usage.get("completion_tokens", 0))
                        span.set_attribute("litellm.total_tokens", usage.get("total_tokens", 0))
                    
                    return result
                    
                except Exception as e:
                    span.set_attribute("error", True)
                    span.set_attribute("exception.type", type(e).__name__)
                    span.set_attribute("exception.message", str(e))
                    raise
        
        # Apply patches
        wrapt.wrap_function_wrapper("litellm", "completion", completion_wrapper)
        wrapt.wrap_function_wrapper("litellm", "acompletion", acompletion_wrapper)
        
        logger.debug("Patched litellm.completion and litellm.acompletion")
    
    def _unpatch_litellm(self):
        """Remove patches from LiteLLM functions."""
        # Unwrap functions if they were wrapped
        if hasattr(litellm.completion, '__wrapped__'):
            litellm.completion = litellm.completion.__wrapped__
        if hasattr(litellm.acompletion, '__wrapped__'):
            litellm.acompletion = litellm.acompletion.__wrapped__
        
        logger.debug("Unpatched litellm.completion and litellm.acompletion")


def _wrap_streaming_response(response, span, api_key, endpoint):
    """Wrap streaming response to collect chunks and update span."""
    collected_content = []
    usage = {}
    
    for chunk in response:
        # Collect content from chunks
        if hasattr(chunk, 'choices') and chunk.choices:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                collected_content.append(delta.content)
        
        # Capture usage if present (usually in last chunk)
        if hasattr(chunk, 'usage') and chunk.usage:
            if hasattr(chunk.usage, 'model_dump'):
                usage = chunk.usage.model_dump()
            elif hasattr(chunk.usage, 'dict'):
                usage = chunk.usage.dict()
            elif isinstance(chunk.usage, dict):
                usage = chunk.usage
        
        yield chunk
    
    # Update span with collected data
    full_content = ''.join(collected_content)
    span.set_attribute("litellm.completion", json.dumps({"content": full_content, "role": "assistant"}))
    
    if usage:
        span.set_attribute("litellm.prompt_tokens", usage.get("prompt_tokens", 0))
        span.set_attribute("litellm.completion_tokens", usage.get("completion_tokens", 0))
        span.set_attribute("litellm.total_tokens", usage.get("total_tokens", 0))


async def _wrap_async_streaming_response(response, span, api_key, endpoint):
    """Wrap async streaming response to collect chunks and update span."""
    collected_content = []
    usage = {}
    
    async for chunk in response:
        # Collect content from chunks
        if hasattr(chunk, 'choices') and chunk.choices:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                collected_content.append(delta.content)
        
        # Capture usage if present (usually in last chunk)
        if hasattr(chunk, 'usage') and chunk.usage:
            if hasattr(chunk.usage, 'model_dump'):
                usage = chunk.usage.model_dump()
            elif hasattr(chunk.usage, 'dict'):
                usage = chunk.usage.dict()
            elif isinstance(chunk.usage, dict):
                usage = chunk.usage
        
        yield chunk
    
    # Update span with collected data
    full_content = ''.join(collected_content)
    span.set_attribute("litellm.completion", json.dumps({"content": full_content, "role": "assistant"}))
    
    if usage:
        span.set_attribute("litellm.prompt_tokens", usage.get("prompt_tokens", 0))
        span.set_attribute("litellm.completion_tokens", usage.get("completion_tokens", 0))
        span.set_attribute("litellm.total_tokens", usage.get("total_tokens", 0))


# =============================================================================
# Legacy Alias
# =============================================================================

class KeywordsAILogger(KeywordsAILiteLLMCallback):
    """Legacy class for backwards compatibility.
    
    Use KeywordsAILiteLLMCallback or LiteLLMInstrumentor instead.
    """
    
    def __init__(self):
        super().__init__()
    
    def log_success(
        self,
        model: str,
        messages: List[Dict],
        response_obj: Any,
        start_time: datetime,
        end_time: datetime,
        print_verbose: callable,
        kwargs: Dict,
    ):
        """Legacy method signature for backwards compatibility."""
        # Reconstruct kwargs format expected by _log_event
        full_kwargs = {
            "model": model,
            "messages": messages,
            "litellm_params": kwargs.get("litellm_params", {}),
            "stream": kwargs.get("stream", False),
            "tools": kwargs.get("tools"),
            "tool_choice": kwargs.get("tool_choice"),
        }
        self._log_event(full_kwargs, response_obj, start_time, end_time, error=None)
