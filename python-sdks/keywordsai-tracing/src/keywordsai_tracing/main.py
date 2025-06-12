import os
import logging
from typing import Optional, Set, Dict, Callable
from opentelemetry.sdk.trace import ReadableSpan

from .decorators import workflow, task, agent, tool
from .core.tracer import KeywordsAITracer
from .core.client import KeywordsAIClient
from .instruments import Instruments
from .contexts.stdio import suppress_stdout


class KeywordsAITelemetry:
    """
    KeywordsAI Telemetry - Direct OpenTelemetry implementation.
    Replaces Traceloop dependency with native OpenTelemetry components.
    
    Args:
        app_name: Name of the application for telemetry identification
        api_key: KeywordsAI API key (can also be set via KEYWORDSAI_API_KEY env var)
        base_url: KeywordsAI API base URL (can also be set via KEYWORDSAI_BASE_URL env var)
        disable_batch: Whether to disable batch span processing (useful for debugging)
        instruments: Set of instruments to enable (if None, enables default set)
        block_instruments: Set of instruments to explicitly disable
        headers: Additional headers to send with telemetry data
        resource_attributes: Additional resource attributes to attach to all spans
        span_postprocess_callback: Optional callback to process spans before export
        enabled: Whether telemetry is enabled (if False, becomes no-op)
        enable_threading_instrumentation: Whether to enable automatic context propagation 
            across threads (default: True). When enabled, OpenTelemetry context flows 
            seamlessly across thread boundaries, ensuring connected traces in multi-threaded 
            applications. This is a global setting that affects all OpenTelemetry context 
            propagation in the process.
    """

    def __init__(
        self,
        app_name: str = "keywordsai",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        disable_batch: Optional[bool] = None,
        instruments: Optional[Set[Instruments]] = None,
        block_instruments: Optional[Set[Instruments]] = None,
        headers: Optional[Dict[str, str]] = None,
        resource_attributes: Optional[Dict[str, str]] = None,
        span_postprocess_callback: Optional[Callable[[ReadableSpan], None]] = None,
        enabled: bool = True,
        enable_threading_instrumentation: bool = True,
    ):
        # Get configuration from environment variables
        api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        base_url = base_url or os.getenv(
            "KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"
        )
        disable_batch = disable_batch or (
            os.getenv("KEYWORDSAI_DISABLE_BATCH", "False").lower() == "true"
        )
        
        # Initialize the tracer
        self.tracer = KeywordsAITracer(
            app_name=app_name,
            api_endpoint=base_url,
            api_key=api_key,
            disable_batch=disable_batch,
            instruments=instruments,
            block_instruments=block_instruments,
            headers=headers,
            resource_attributes=resource_attributes,
            span_postprocess_callback=span_postprocess_callback,
            enabled=enabled,
            enable_threading_instrumentation=enable_threading_instrumentation,
        )
        
        if enabled:
            logging.info(f"KeywordsAI telemetry initialized, sending to {base_url}")
        else:
            logging.info("KeywordsAI telemetry is disabled")

    def flush(self):
        """Force flush all pending spans"""
        self.tracer.flush()
    
    def is_initialized(self) -> bool:
        """Check if telemetry is initialized"""
        return KeywordsAITracer.is_initialized()

    def get_client(self) -> KeywordsAIClient:
        """
        Get a client for interacting with the current trace/span context.
        
        Returns:
            KeywordsAIClient instance for trace operations.
        """
        return KeywordsAIClient()

    # Expose decorators as instance methods for backward compatibility
    workflow = staticmethod(workflow)
    task = staticmethod(task)
    agent = staticmethod(agent)
    tool = staticmethod(tool)


# Module-level client instance for global access
_global_client: Optional[KeywordsAIClient] = None


def get_client() -> KeywordsAIClient:
    """
    Get a global KeywordsAI client instance.
    
    This function provides access to trace operations without needing to maintain
    a reference to the KeywordsAITelemetry instance. The client uses the singleton
    tracer instance internally.
    
    Returns:
        KeywordsAIClient instance for trace operations.
        
    Example:
        ```python
        from keywordsai_tracing import get_client
        
        client = get_client()
        
        # Get current trace information
        trace_id = client.get_current_trace_id()
        span_id = client.get_current_span_id()
        
        # Update current span
        client.update_current_span(
            keywordsai_params={"trace_group_identifier": "my-group"},
            attributes={"custom.attribute": "value"}
        )
        
        # Add events and handle exceptions
        client.add_event("processing_started")
        try:
            # Your code here
            pass
        except Exception as e:
            client.record_exception(e)
        ```
    """
    global _global_client
    if _global_client is None:
        _global_client = KeywordsAIClient()
    return _global_client



