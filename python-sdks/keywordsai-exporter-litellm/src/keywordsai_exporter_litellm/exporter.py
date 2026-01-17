"""Keywords AI LiteLLM Integration.

Two integration methods:
1. LiteLLMInstrumentor - OpenTelemetry-compliant automatic instrumentation
2. KeywordsAILiteLLMCallback - LiteLLM-native callback class
"""

import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Collection, Dict, List, Optional

import litellm
import requests
import wrapt
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult

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
    """OTEL SpanExporter that sends spans to Keywords AI."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 10,
    ):
        self.api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        self.endpoint = endpoint or os.getenv("KEYWORDSAI_ENDPOINT", DEFAULT_KEYWORDSAI_ENDPOINT)
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning("Keywords AI API key not provided")
    
    def export(self, spans) -> SpanExportResult:
        """Export spans to Keywords AI endpoint."""
        if not self.api_key:
            return SpanExportResult.FAILURE
        
        try:
            payloads = [p for s in spans if (p := self._transform_span(s))]
            if payloads:
                self._send_batch(payloads)
            return SpanExportResult.SUCCESS
        except Exception as e:
            logger.error(f"Failed to export spans: {e}")
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        pass
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
    
    def _transform_span(self, span) -> Optional[Dict[str, Any]]:
        """Transform OTEL span to Keywords AI format."""
        attrs = dict(span.attributes) if span.attributes else {}
        
        # Timestamps
        start_ns, end_ns = span.start_time, span.end_time
        start_iso = datetime.fromtimestamp(start_ns / 1e9, tz=timezone.utc).isoformat()
        end_iso = datetime.fromtimestamp(end_ns / 1e9, tz=timezone.utc).isoformat()
        
        # Determine log_type
        is_llm = span.name.startswith("litellm")
        log_type = "generation" if is_llm else ("tool" if span.parent else "workflow")
        
        payload = {
            "trace_unique_id": format(span.context.trace_id, '032x'),
            "span_unique_id": format(span.context.span_id, '016x'),
            "span_name": span.name,
            "span_workflow_name": attrs.get("workflow.name", span.name),
            "log_type": log_type,
            "timestamp": end_iso,
            "start_time": start_iso,
            "latency": (end_ns - start_ns) / 1e9,
        }
        
        if span.parent:
            payload["span_parent_id"] = format(span.parent.span_id, '016x')
        
        # Model
        if model := attrs.get("litellm.model") or attrs.get("llm.model"):
            payload["model"] = model
        
        # Input/Output
        if "litellm.messages" in attrs:
            msg = attrs["litellm.messages"]
            payload["input"] = msg if isinstance(msg, str) else json.dumps(msg)
        
        if "litellm.completion" in attrs:
            comp = attrs["litellm.completion"]
            payload["output"] = comp if isinstance(comp, str) else json.dumps(comp)
        
        # Usage
        usage = {}
        for key in ["prompt_tokens", "completion_tokens", "total_tokens"]:
            if f"litellm.{key}" in attrs:
                usage[key] = attrs[f"litellm.{key}"]
        if usage:
            payload["usage"] = usage
        
        # Error
        if attrs.get("error"):
            payload["error_message"] = attrs.get("exception.message", str(attrs.get("error")))
            payload["status"] = "error"
        
        # Stream/Tools
        if "litellm.stream" in attrs:
            payload["stream"] = attrs["litellm.stream"]
        
        for key in ["tools", "tool_choice"]:
            if f"litellm.{key}" in attrs:
                val = attrs[f"litellm.{key}"]
                if isinstance(val, str):
                    try:
                        val = json.loads(val)
                    except json.JSONDecodeError:
                        pass
                payload[key] = val
        
        # Keywords AI params
        metadata = {}
        for key, value in attrs.items():
            if key.startswith("keywordsai."):
                param = key.replace("keywordsai.", "")
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                
                if param == "customer_identifier":
                    payload["customer_identifier"] = value
                elif param == "customer_params" and isinstance(value, dict):
                    payload["customer_identifier"] = value.get("customer_identifier")
                    for k, v in value.items():
                        if k != "customer_identifier":
                            metadata[f"customer_{k}"] = v
                elif param == "thread_identifier":
                    payload["thread_identifier"] = value
                elif param == "metadata" and isinstance(value, dict):
                    metadata.update(value)
                else:
                    metadata[param] = value
        
        if metadata:
            payload["metadata"] = metadata
        
        return payload
    
    def _send_batch(self, payloads: List[Dict[str, Any]]) -> None:
        """Send batch to Keywords AI."""
        response = requests.post(
            self.endpoint,
            json=payloads,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        if response.status_code != 200:
            logger.warning(f"Keywords AI API error: {response.status_code}")


# =============================================================================
# LiteLLM Callback
# =============================================================================

class KeywordsAILiteLLMCallback:
    """LiteLLM callback that sends logs to Keywords AI.
    
    Usage:
        callback = KeywordsAILiteLLMCallback(api_key="...")
        litellm.success_callback = [callback.log_success_event]
        litellm.failure_callback = [callback.log_failure_event]
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 10,
    ):
        self.api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        self.endpoint = endpoint or os.getenv("KEYWORDSAI_ENDPOINT", DEFAULT_KEYWORDSAI_ENDPOINT)
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning("Keywords AI API key not provided")
    
    def log_success_event(self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime) -> None:
        """Log successful completion."""
        self._log_event(kwargs, response_obj, start_time, end_time, error=None)
    
    async def async_log_success_event(self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime) -> None:
        """Async log successful completion."""
        threading.Thread(target=self._log_event, args=(kwargs, response_obj, start_time, end_time, None)).start()
    
    def log_failure_event(self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime) -> None:
        """Log failed completion."""
        error = kwargs.get("exception") or kwargs.get("traceback_exception")
        self._log_event(kwargs, response_obj, start_time, end_time, error=error)
    
    async def async_log_failure_event(self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime) -> None:
        """Async log failed completion."""
        error = kwargs.get("exception") or kwargs.get("traceback_exception")
        threading.Thread(target=self._log_event, args=(kwargs, response_obj, start_time, end_time, error)).start()
    
    def _to_utc_iso(self, dt: datetime) -> str:
        """Convert datetime to UTC ISO string."""
        if dt.tzinfo is None:
            dt = dt.astimezone(timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.isoformat()
    
    def _log_event(self, kwargs: Dict, response_obj: Any, start_time: datetime, end_time: datetime, error: Optional[Exception]) -> None:
        """Send event to Keywords AI."""
        if not self.api_key:
            return
        
        try:
            model = kwargs.get("model") or kwargs.get("litellm_params", {}).get("model")
            messages = kwargs.get("messages", [])
            metadata = kwargs.get("litellm_params", {}).get("metadata", {}) or {}
            kw_params = metadata.get("keywordsai_params", {})
            
            payload = {
                "trace_unique_id": kw_params.get("trace_id") or uuid.uuid4().hex,
                "span_unique_id": kw_params.get("span_id") or uuid.uuid4().hex[:16],
                "span_name": kw_params.get("span_name", "litellm.completion"),
                "span_workflow_name": kw_params.get("workflow_name", "litellm"),
                "log_type": "generation",
                "timestamp": self._to_utc_iso(end_time),
                "start_time": self._to_utc_iso(start_time),
                "latency": (end_time - start_time).total_seconds(),
                "model": model,
                "input": json.dumps(messages),
                "stream": kwargs.get("stream", False),
            }
            
            if parent_id := kw_params.get("parent_span_id"):
                payload["span_parent_id"] = parent_id
            
            if kwargs.get("tools"):
                payload["tools"] = kwargs["tools"]
            if kwargs.get("tool_choice"):
                payload["tool_choice"] = kwargs["tool_choice"]
            
            if error:
                payload["status"] = "error"
                payload["error_message"] = str(error)
            else:
                payload["status"] = "success"
                if response_obj:
                    resp = self._extract_response(response_obj)
                    if choices := resp.get("choices", []):
                        payload["output"] = json.dumps(choices[0].get("message", {}))
                    if usage := resp.get("usage", {}):
                        payload["usage"] = {
                            "prompt_tokens": usage.get("prompt_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "total_tokens": usage.get("total_tokens"),
                        }
            
            # Extract Keywords AI params
            extra_meta = {}
            if "customer_identifier" in kw_params:
                payload["customer_identifier"] = kw_params["customer_identifier"]
            if cp := kw_params.get("customer_params"):
                if isinstance(cp, dict):
                    payload["customer_identifier"] = cp.get("customer_identifier")
                    extra_meta.update({f"customer_{k}": v for k, v in cp.items() if k != "customer_identifier"})
            if "thread_identifier" in kw_params:
                payload["thread_identifier"] = kw_params["thread_identifier"]
            if m := kw_params.get("metadata"):
                if isinstance(m, dict):
                    extra_meta.update(m)
            
            excluded = ("customer_identifier", "customer_params", "thread_identifier", "metadata", 
                       "workflow_name", "trace_id", "span_id", "parent_span_id", "span_name")
            extra_meta.update({k: v for k, v in kw_params.items() if k not in excluded})
            
            if extra_meta:
                payload["metadata"] = extra_meta
            
            self._send([payload])
        except Exception as e:
            logger.error(f"Keywords AI logging error: {e}")
    
    def _extract_response(self, response_obj: Any) -> Dict:
        """Extract dict from response object."""
        if hasattr(response_obj, "model_dump"):
            return response_obj.model_dump(mode="json")
        if hasattr(response_obj, "dict"):
            return response_obj.dict()
        if isinstance(response_obj, dict):
            return response_obj
        return {}
    
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
        """Send a workflow span to Keywords AI."""
        if not self.api_key:
            return
        
        try:
            now = datetime.now(timezone.utc)
            start = start_time or now
            end = end_time or now
            
            payload = {
                "trace_unique_id": trace_id,
                "span_unique_id": span_id,
                "span_name": workflow_name,
                "span_workflow_name": workflow_name,
                "log_type": "workflow",
                "timestamp": end.isoformat() if hasattr(end, 'isoformat') else str(end),
                "start_time": start.isoformat() if hasattr(start, 'isoformat') else str(start),
                "latency": (end - start).total_seconds() if end_time else 0.0,
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
            
            self._send([payload])
        except Exception as e:
            logger.error(f"Keywords AI workflow span error: {e}")
    
    def _send(self, payloads: List[Dict[str, Any]]) -> None:
        """Send payloads to Keywords AI."""
        try:
            response = requests.post(
                self.endpoint,
                json=payloads,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
            if response.status_code != 200:
                logger.warning(f"Keywords AI error: {response.status_code}")
        except Exception as e:
            logger.error(f"Keywords AI request error: {e}")


# =============================================================================
# OTEL Instrumentor
# =============================================================================

class LiteLLMInstrumentor(BaseInstrumentor):
    """OpenTelemetry instrumentor for LiteLLM.
    
    Usage:
        LiteLLMInstrumentor().instrument(api_key="...")
        response = litellm.completion(model="gpt-4", messages=[...])
    """
    
    _api_key: Optional[str] = None
    _endpoint: Optional[str] = None
    _tracer_provider: Optional[TracerProvider] = None
    _tracer: Optional[trace.Tracer] = None
    _exporter: Optional[KeywordsAISpanExporter] = None
    
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments
    
    def _instrument(self, **kwargs):
        """Enable instrumentation."""
        self._api_key = kwargs.get("api_key") or os.getenv("KEYWORDSAI_API_KEY")
        self._endpoint = kwargs.get("endpoint") or os.getenv("KEYWORDSAI_ENDPOINT", DEFAULT_KEYWORDSAI_ENDPOINT)
        
        if not self._api_key:
            logger.warning("Keywords AI API key not provided")
            return
        
        tracer_provider = kwargs.get("tracer_provider")
        if tracer_provider is None:
            self._exporter = KeywordsAISpanExporter(api_key=self._api_key, endpoint=self._endpoint)
            resource = Resource.create({"service.name": kwargs.get("service_name", "litellm-service")})
            self._tracer_provider = TracerProvider(resource=resource)
            self._tracer_provider.add_span_processor(SimpleSpanProcessor(self._exporter))
            trace.set_tracer_provider(self._tracer_provider)
        else:
            self._tracer_provider = tracer_provider
        
        self._tracer = trace.get_tracer(__name__)
        self._patch()
    
    def _uninstrument(self, **kwargs):
        """Disable instrumentation."""
        self._unpatch()
        if self._tracer_provider:
            self._tracer_provider.force_flush()
            self._tracer_provider.shutdown()
            self._tracer_provider = None
        self._tracer = None
        self._exporter = None
    
    def flush(self):
        """Force flush pending spans."""
        if self._tracer_provider:
            self._tracer_provider.force_flush()
    
    def _patch(self):
        """Patch LiteLLM functions."""
        tracer = self._tracer
        
        def completion_wrapper(wrapped, instance, args, kwargs):
            model = kwargs.get("model") or (args[0] if args else "unknown")
            messages = kwargs.get("messages", [])
            stream = kwargs.get("stream", False)
            
            with tracer.start_as_current_span("litellm.completion", kind=trace.SpanKind.CLIENT) as span:
                span.set_attribute("litellm.model", model)
                span.set_attribute("litellm.stream", stream)
                span.set_attribute("litellm.messages", json.dumps(messages))
                
                if kwargs.get("tools"):
                    span.set_attribute("litellm.tools", json.dumps(kwargs["tools"]))
                if tc := kwargs.get("tool_choice"):
                    span.set_attribute("litellm.tool_choice", json.dumps(tc) if isinstance(tc, dict) else str(tc))
                
                # Keywords AI params
                kw_params = (kwargs.get("metadata") or {}).get("keywordsai_params", {})
                for key, value in kw_params.items():
                    span.set_attribute(f"keywordsai.{key}", json.dumps(value) if isinstance(value, (dict, list)) else value)
                
                try:
                    result = wrapped(*args, **kwargs)
                    if stream:
                        return _wrap_streaming(result, span)
                    
                    resp = self._extract_response(result)
                    if choices := resp.get("choices", []):
                        span.set_attribute("litellm.completion", json.dumps(choices[0].get("message", {})))
                    if usage := resp.get("usage", {}):
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
            model = kwargs.get("model") or (args[0] if args else "unknown")
            messages = kwargs.get("messages", [])
            stream = kwargs.get("stream", False)
            
            with tracer.start_as_current_span("litellm.acompletion", kind=trace.SpanKind.CLIENT) as span:
                span.set_attribute("litellm.model", model)
                span.set_attribute("litellm.stream", stream)
                span.set_attribute("litellm.messages", json.dumps(messages))
                
                if kwargs.get("tools"):
                    span.set_attribute("litellm.tools", json.dumps(kwargs["tools"]))
                if tc := kwargs.get("tool_choice"):
                    span.set_attribute("litellm.tool_choice", json.dumps(tc) if isinstance(tc, dict) else str(tc))
                
                kw_params = (kwargs.get("metadata") or {}).get("keywordsai_params", {})
                for key, value in kw_params.items():
                    span.set_attribute(f"keywordsai.{key}", json.dumps(value) if isinstance(value, (dict, list)) else value)
                
                try:
                    result = await wrapped(*args, **kwargs)
                    if stream:
                        return _wrap_async_streaming(result, span)
                    
                    resp = self._extract_response(result)
                    if choices := resp.get("choices", []):
                        span.set_attribute("litellm.completion", json.dumps(choices[0].get("message", {})))
                    if usage := resp.get("usage", {}):
                        span.set_attribute("litellm.prompt_tokens", usage.get("prompt_tokens", 0))
                        span.set_attribute("litellm.completion_tokens", usage.get("completion_tokens", 0))
                        span.set_attribute("litellm.total_tokens", usage.get("total_tokens", 0))
                    return result
                except Exception as e:
                    span.set_attribute("error", True)
                    span.set_attribute("exception.type", type(e).__name__)
                    span.set_attribute("exception.message", str(e))
                    raise
        
        wrapt.wrap_function_wrapper("litellm", "completion", completion_wrapper)
        wrapt.wrap_function_wrapper("litellm", "acompletion", acompletion_wrapper)
    
    def _unpatch(self):
        """Remove patches."""
        if hasattr(litellm.completion, '__wrapped__'):
            litellm.completion = litellm.completion.__wrapped__
        if hasattr(litellm.acompletion, '__wrapped__'):
            litellm.acompletion = litellm.acompletion.__wrapped__
    
    def _extract_response(self, result: Any) -> Dict:
        """Extract dict from response."""
        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        if hasattr(result, "dict"):
            return result.dict()
        if isinstance(result, dict):
            return result
        return {}


# =============================================================================
# Streaming Helpers
# =============================================================================

def _wrap_streaming(response, span):
    """Wrap streaming response."""
    content = []
    usage = {}
    
    for chunk in response:
        if hasattr(chunk, 'choices') and chunk.choices:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                content.append(delta.content)
        if hasattr(chunk, 'usage') and chunk.usage:
            usage = chunk.usage.model_dump() if hasattr(chunk.usage, 'model_dump') else (
                chunk.usage.dict() if hasattr(chunk.usage, 'dict') else chunk.usage
            )
        yield chunk
    
    span.set_attribute("litellm.completion", json.dumps({"content": ''.join(content), "role": "assistant"}))
    if usage:
        span.set_attribute("litellm.prompt_tokens", usage.get("prompt_tokens", 0))
        span.set_attribute("litellm.completion_tokens", usage.get("completion_tokens", 0))
        span.set_attribute("litellm.total_tokens", usage.get("total_tokens", 0))


async def _wrap_async_streaming(response, span):
    """Wrap async streaming response."""
    content = []
    usage = {}
    
    async for chunk in response:
        if hasattr(chunk, 'choices') and chunk.choices:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                content.append(delta.content)
        if hasattr(chunk, 'usage') and chunk.usage:
            usage = chunk.usage.model_dump() if hasattr(chunk.usage, 'model_dump') else (
                chunk.usage.dict() if hasattr(chunk.usage, 'dict') else chunk.usage
            )
        yield chunk
    
    span.set_attribute("litellm.completion", json.dumps({"content": ''.join(content), "role": "assistant"}))
    if usage:
        span.set_attribute("litellm.prompt_tokens", usage.get("prompt_tokens", 0))
        span.set_attribute("litellm.completion_tokens", usage.get("completion_tokens", 0))
        span.set_attribute("litellm.total_tokens", usage.get("total_tokens", 0))


# =============================================================================
# Legacy Alias
# =============================================================================

class KeywordsAILogger(KeywordsAILiteLLMCallback):
    """Legacy class for backwards compatibility."""
    
    def log_success(self, model: str, messages: List[Dict], response_obj: Any, 
                   start_time: datetime, end_time: datetime, print_verbose: callable, kwargs: Dict):
        full_kwargs = {
            "model": model, "messages": messages,
            "litellm_params": kwargs.get("litellm_params", {}),
            "stream": kwargs.get("stream", False),
            "tools": kwargs.get("tools"),
            "tool_choice": kwargs.get("tool_choice"),
        }
        self._log_event(full_kwargs, response_obj, start_time, end_time, error=None)
